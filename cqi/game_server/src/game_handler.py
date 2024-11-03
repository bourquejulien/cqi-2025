from dataclasses import dataclass
from enum import Enum
import requests
import random
from logging import Logger

from .map import Map, Position, ElementType
from .offense_player import OffensePlayer
from .defense_player import DefensePlayer, DefenseMove

START_ENDPOINT = "/start"
NEXT_ENDPOINT = "/next_move"
END_ENDPOINT = "/end_game"
ORIENTATION = ["UP", "DOWN", "RIGHT", "LEFT"]


@dataclass
class GameStatus:
    map: list


class GameHandler:
    logger: Logger

    offense_bot_url: str
    defense_bot_url: str

    map: Map
    offense_player: OffensePlayer | None
    defense_player: DefensePlayer | None
    goal: Position
    move_count: int

    def __init__(self, offense_bot_url: str, defense_bot_url: str, logger: Logger) -> None:
        self.logger = logger
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map(
            random.randint(20, 40), random.randint(20, 40))
        self.goal = self.map.set_goal()

        self.offense_player = None
        self.move_count = 50
    
    @property
    def is_started(self) -> bool:
        return self.offense_player is not None

    @property
    def is_over(self) -> bool:
        return False

    def play(self):
        self._play_defense()
        self._play_offense()

    def end_game(self):
        requests.post(self.offense_bot_url + END_ENDPOINT, {})
        requests.post(self.defense_bot_url + END_ENDPOINT, {})

    def start_game(self):
        self.offense_player = OffensePlayer(self.map)
        self.defense_player = DefensePlayer(self.map)
        requests.post(self.offense_bot_url + START_ENDPOINT,
                      json={"is_offense": True})
        requests.post(self.defense_bot_url + START_ENDPOINT,
                      json={"is_offense": False})

    def _play_defense(self):
        response: requests.Response = requests.post(self.defense_bot_url + NEXT_ENDPOINT, json={
                                                    "map": self.map.to_img_64(self.offense_player.position).decode()})

        # Parse response
        try:
            response_json = response.json()

            x = response_json["x"]
            assert isinstance(x, int)

            y = response_json["y"]
            assert isinstance(y, int)

            if response_json["element"] == "WALL":
                element = ElementType.WALL
            else:
                self.logger.info(
                    f"Defense bot returned invalid element: {response_json['element']}")
                return

            move = DefenseMove(Position(x, y), element)

        except Exception as e:
            self.logger.error(f"Error parsing response from defense bot: {e}")
            return

        self.defense_player.move(logger=self.logger,
                                 move=move,
                                 player=self.offense_player.position,
                                 goal=self.goal)

    def _play_offense(self):
        response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={"map": self.map.to_img_64(self.offense_player.position, 3).decode()})

        try:
            data = response.json()
            assert isinstance(data["move"], str)
        except Exception as e:
            self.logger.error(f"Error parsing response from offense bot: {e}")
            return

        self.move_count -= 1
        if self.move_count < 0:
            return

        values = [item.value for item in ORIENTATION]
        if data["move"] not in values:
            return
        
        previous_offense_position = self.offense_player.position
        
        match(data["move"]):
            case "UP":
                self.offense_player.position.y += 1
            case "DOWN":
                self.offense_player.position.y -= 1
            case "RIGHT":
                self.offense_player.position.x += 1
            case "LEFT":
                self.offense_player.position.x -= 1

        width_map_bounds = self.offense_player.position.x < self.map.width or self.offense_player.position.x > self.map.width
        heigth_map_bounds = self.offense_player.position.y < self.map.height or self.offense_player.position.y > self.map.height

        if width_map_bounds or heigth_map_bounds:
            self.offense_player.position = previous_offense_position

        if self.offense_player.position.x and self.offense_player.position.y != ElementType.BACKGROUND.value or ElementType.GOAL.value:
            self.offense_player.position = previous_offense_position

    def get_status(self) -> GameStatus:
        return GameStatus(self.map.to_list())
