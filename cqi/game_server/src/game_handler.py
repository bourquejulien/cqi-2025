from dataclasses import dataclass
from typing import Iterator
import requests
import random
import logging

from game_server_common.base import OffenseMove
from .map import Map, Position, ElementType
from .offense_player import OffensePlayer
from .defense_player import DefensePlayer, DefenseMove
from .logger import GameStep, Level, Logger

START_ENDPOINT = "/start"
NEXT_ENDPOINT = "/next_move"
END_ENDPOINT = "/end_game"

N_WALLS = 30
N_TIMEBOMBS = 1
TIMEOUT = 10
MIN_MAP_SIZE = 20
MAX_MAP_SIZE = 40

N_FULL_VISION = 3

@dataclass
class GameData:
    steps: list[GameStep]
    error_message: str | None
    max_move_count: int

    def __iter__(self) -> Iterator:
        yield "steps", [dict(step) for step in self.steps]
        yield "errorMessage", self.error_message
        yield "maxMoveCount", self.max_move_count

class GameHandler:
    offense_bot_url: str
    defense_bot_url: str

    map: Map
    max_move: int
    goal: Position
    timebomb: Position | None

    offense_player: OffensePlayer | None
    defense_player: DefensePlayer | None

    logger: Logger
    error_message: str | None

    timebomb_countdown: int

    def __init__(self, offense_bot_url: str, defense_bot_url: str, max_move: int | None) -> None:
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map(random.randint(MIN_MAP_SIZE, MAX_MAP_SIZE), random.randint(MIN_MAP_SIZE, MAX_MAP_SIZE))
        self.max_move = max_move or (self.map.width + self.map.height) * 4

        self.goal = self.map.set_goal()

        for _ in range(N_FULL_VISION):
            self.map.set_full_vision()

        self.offense_player = None
        self.defense_player = None

        self.logger = Logger()
        self.error_message = None

        self.timebomb_countdown = -1

    @property
    def move_count(self) -> int:
        return len(self.logger.get())
        
    @property
    def available_moves(self) -> int:
        return self.max_move - self.move_count

    @available_moves.setter
    def available_moves(self, value: int) -> None:
        self.max_move = value + self.move_count

    @property
    def score(self) -> int | None:
        if self.goal is None or self.offense_player is None:
            return None

        shortest_path = self.map.get_shortest_path(
            self.offense_player.position, self.goal)
        return self.max_move - len(shortest_path) + (self.max_move - self.move_count)

    @property
    def is_started(self) -> bool:
        return self.offense_player is not None and self.defense_player is not None

    @property
    def is_over(self) -> bool:
        if self.goal is None or self.offense_player is None:
            return False

        if self.available_moves <= 0 or self.error_message is not None:
            return True

        return self.goal == self.offense_player.position

    def play(self):
        self.logger.add(f"Remaining number of moves: {self.available_moves}", Level.DEBUG)

        self._play_defense()
        self._play_offense()

        self.logger.add_step(self.map.to_list(), self.score, self.offense_player.get_vision_radius())

    def end_game(self):
        try:
            requests.post(self.offense_bot_url + END_ENDPOINT, {})
            requests.post(self.defense_bot_url + END_ENDPOINT, {})
        except Exception as e:
            logging.error(f"Error ending game: {e}")

    def start_game(self):
        self.offense_player = OffensePlayer(self.map)
        self.defense_player = DefensePlayer(self.map, n_walls=N_WALLS, n_timebombs=N_TIMEBOMBS)

        self.logger.add(f"Starting game, Goal position: {self.goal}", Level.INFO)

        try:
            element_types_color = {
                "background": ElementType.BACKGROUND.to_color(), 
                "wall": ElementType.WALL.to_color(), 
                "offense_player": ElementType.PLAYER_OFFENSE.to_color(), 
                "goal": ElementType.GOAL.to_color(), 
                "large_vision": ElementType.LARGE_VISION.to_color(), 
                "timebomb": ElementType.TIMEBOMB.to_color(), 
                "timebomb_second_round": ElementType.TIMEBOMB_SECOND_ROUND.to_color(), 
                "timebomb_third_round": ElementType.TIMEBOMB_THIRD_ROUND.to_color()
            }

            result = requests.post(self.offense_bot_url + START_ENDPOINT,
                                   json={"is_offense": True, "max_moves": self.max_move, "element_types_color": element_types_color}, timeout=TIMEOUT)
            result.raise_for_status()

            result = requests.post(self.defense_bot_url + START_ENDPOINT,
                                   json={"is_offense": False, "n_walls": N_WALLS, "element_types_color": element_types_color}, timeout=TIMEOUT)
            result.raise_for_status()
        except Exception as e:
            logging.error(f"Error starting game: {e}")
            self.error_message = f"Failed to start game with exception:\n{
                str(e)}"
            return
        
        self.logger.add_step(self.map.to_list(), self.score, self.offense_player.get_vision_radius())


    def _play_defense(self):
        try:
            response: requests.Response = requests.post(self.defense_bot_url + NEXT_ENDPOINT, json={
                                                    "map": self.map.to_img_64(self.offense_player.position).decode()}, timeout=TIMEOUT)
        except Exception as e:
            self.logger.add(f"Error getting response from defense bot: {e}", Level.ERROR)
            return

        try:
            response_json = response.json()

            x = response_json["x"]
            assert isinstance(x, int)

            y = response_json["y"]
            assert isinstance(y, int)

            if response_json["element"] == "wall":
                element = ElementType.WALL
            elif response_json["element"] == "skip":
                self.logger.add("Defense move was skipped", Level.INFO)
                return
            elif response_json["element"] == "timebomb":
                element = ElementType.TIMEBOMB
            else:
                self.logger.add(f"Defense bot returned invalid element: {response_json['element']}", Level.INFO)
                return

            move = DefenseMove(Position(x, y), element)

        except Exception as e:
            self.logger.add(f"Error parsing response from defense bot: {e}\n{response}", Level.ERROR)
            return

        is_move_valid = self.defense_player.move(move=move,
                                 player=self.offense_player.position,
                                 goal=self.goal)
        
        if is_move_valid and element == ElementType.TIMEBOMB:
            self.timebomb = Position(x, y)
            self.timebomb_countdown = 2

    def _play_offense(self):
        try:
            response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={
                                    "map": self.map.to_img_64(self.offense_player.position, self.offense_player.get_vision_radius()).decode()}, timeout=TIMEOUT)
        except Exception as e:
            self.logger.add(f"Error getting response from offense bot: {e}", Level.ERROR)
            return

        move: OffenseMove
        try:
            data = response.json()
            move = OffenseMove(data["move"])
        except Exception as e:
            self.logger.add(f"Error parsing response from offense bot: {e}\n{response}", Level.ERROR)
            return

        if move is None:
            self.logger.add("Offense move was skipped", Level.INFO)
            return

        if self.available_moves <= 0:
            self.logger.add("No more move available", Level.INFO)
            return

        offset = move.to_position()
        previous_offense_position = self.offense_player.position
        self.offense_player.position = self.offense_player.position + offset

        next_tile = self.map.get(
            self.offense_player.position.x, self.offense_player.position.y)

        if next_tile is None:
            self.logger.add(f"Offense move out of bounds: {self.offense_player.position}", Level.INFO)
            self.offense_player.position = previous_offense_position
            return

        if next_tile.element not in [ElementType.BACKGROUND, ElementType.GOAL, ElementType.LARGE_VISION, ElementType.PLAYER_OFFENSE]:
            self.logger.add(f"Offense move not on a valid map element: {self.offense_player.position} is a {next_tile}", Level.INFO)
            self.offense_player.position = previous_offense_position
            return

        self.logger.add(f"Previous offense position: {previous_offense_position}, Goal position: {self.goal}", Level.DEBUG)

        self.logger.add("Offense move valid", Level.INFO)
        self.map.set(previous_offense_position.x, previous_offense_position.y, ElementType.BACKGROUND)
        self.map.set(self.offense_player.position.x, self.offense_player.position.y, ElementType.PLAYER_OFFENSE)

        self.logger.add(f"Offense new position is: {self.offense_player.position}", Level.DEBUG)

        match self.timebomb_countdown:
            case 2:
                self.timebomb_countdown -= 1
                self.map.set(self.timebomb.x, self.timebomb.y, ElementType.TIMEBOMB_SECOND_ROUND)
            case 1:
                self.timebomb_countdown -= 1
                self.map.set(self.timebomb.x, self.timebomb.y, ElementType.TIMEBOMB_THIRD_ROUND)
            case 0:
                self.map.set(self.timebomb.x, self.timebomb.y, ElementType.BACKGROUND)
                radius = abs(self.offense_player.position.x - self.timebomb.x) <= 1 and abs(self.offense_player.position.y - self.timebomb.y) <= 1
                if self.offense_player.position == self.timebomb or (self.timebomb and radius):
                    self.available_moves = max(0, self.available_moves - 10)
                    return

    def get_data(self) -> GameData:
        return GameData(
            steps=self.logger.get(),
            error_message=self.error_message,
            max_move_count=self.max_move)
