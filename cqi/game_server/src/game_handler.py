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
MAX_MOVES = 200
TIMEOUT = 10
MIN_MAP_SIZE = 20
MAX_MAP_SIZE = 40


@dataclass
class GameData:
    steps: list[GameStep]
    error_message: str | None

    def __iter__(self) -> Iterator:
        yield "steps", [dict(step) for step in self.steps]
        yield "errorMessage", self.error_message


class GameHandler:
    offense_bot_url: str
    defense_bot_url: str

    map: Map
    offense_player: OffensePlayer | None
    defense_player: DefensePlayer | None
    goal: Position
    large_vision: Position

    logger: Logger
    error_message: str | None

    def __init__(self, offense_bot_url: str, defense_bot_url: str, seed: str) -> None:
        random.seed(seed)
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map(random.randint(MIN_MAP_SIZE, MAX_MAP_SIZE), random.randint(MIN_MAP_SIZE, MAX_MAP_SIZE))
        self.goal = self.map.set_goal()
        self.large_vision = self.map.set_large_vision()
        while self.large_vision == self.goal:
            self.large_vision = self.map.set_large_vision()

        self.offense_player = None
        self.defense_player = None

        self.error_message = None
        self.logger = Logger()

    @property
    def available_moves(self) -> int:
        return MAX_MOVES - len(self.logger.get())    

    @property
    def score(self) -> int | None:
        if self.goal is None or self.offense_player is None:
            return None

        shortest_path = self.map.get_shortest_path(
            self.offense_player.position, self.goal)
        return MAX_MOVES - len(shortest_path) + (MAX_MOVES - self.available_moves)

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

        self.logger.add_step(self.map.to_list(), self.score)

    def end_game(self):
        try:
            requests.post(self.offense_bot_url + END_ENDPOINT, {})
            requests.post(self.defense_bot_url + END_ENDPOINT, {})
        except Exception as e:
            logging.error(f"Error ending game: {e}")

    def start_game(self):
        self.offense_player = OffensePlayer(self.map)
        self.defense_player = DefensePlayer(self.map, n_walls=N_WALLS)

        self.logger.add(f"Starting game, Goal position: {self.goal}", Level.INFO)

        try:
            element_types_color = {"background": ElementType.BACKGROUND.to_color(), "wall": ElementType.WALL.to_color(), "offense_player": ElementType.PLAYER_OFFENSE.to_color(), "goal": ElementType.GOAL.to_color(), "large_vision": ElementType.LARGE_VISION.to_color()}

            result = requests.post(self.offense_bot_url + START_ENDPOINT,
                                   json={"is_offense": True, "max_moves": MAX_MOVES, "element_types_color": element_types_color}, timeout=TIMEOUT)
            result.raise_for_status()

            result = requests.post(self.defense_bot_url + START_ENDPOINT,
                                   json={"is_offense": False, "n_walls": N_WALLS, "element_types_color": element_types_color}, timeout=TIMEOUT)
            result.raise_for_status()
        except Exception as e:
            logging.error(f"Error starting game: {e}")
            self.error_message = f"Failed to start game with exception:\n{
                str(e)}"
            return
        
        self.logger.add_step(self.map.to_list(), self.score)

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
            else:
                self.logger.add(f"Defense bot returned invalid element: {response_json['element']}", Level.INFO)
                return

            move = DefenseMove(Position(x, y), element)

        except Exception as e:
            self.logger.add(f"Error parsing response from defense bot: {e}\n{response}", Level.ERROR)
            return

        self.defense_player.move(move=move,
                                 player=self.offense_player.position,
                                 goal=self.goal)

    def _play_offense(self):
        try:
            if self.offense_player.position == self.large_vision:
                response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={
                                    "map": self.map.to_img_64(self.offense_player.position, 5).decode()}, timeout=TIMEOUT)
            else:
                response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={
                                    "map": self.map.to_img_64(self.offense_player.position, 3).decode()}, timeout=TIMEOUT)
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

        if next_tile.element not in [ElementType.BACKGROUND, ElementType.GOAL, ElementType.LARGE_VISION]:
            self.logger.add(f"Offense move not on a valid map element: {self.offense_player.position} is a {next_tile}", Level.INFO)
            self.offense_player.position = previous_offense_position
            return

        self.logger.add(f"Previous offense position: {previous_offense_position}, Goal position: {self.goal}", Level.DEBUG)

        self.logger.add("Offense move valid", Level.INFO)
        self.map.set(previous_offense_position.x, previous_offense_position.y, ElementType.BACKGROUND)
        self.map.set(self.offense_player.position.x, self.offense_player.position.y, ElementType.PLAYER_OFFENSE)

        self.logger.add(f"Offense new position is: {self.offense_player.position}", Level.DEBUG)

    def get_data(self) -> GameData:
        return GameData(self.logger.get(), error_message=self.error_message)
