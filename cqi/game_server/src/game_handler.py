from dataclasses import dataclass
from enum import Enum
import requests
import random
from logging import Logger

from .map import Map, Position
from .offense_player import OffensePlayer
from .defense_player import DefensePlayer

START_ENDPOINT = "/start"
NEXT_ENDPOINT = "/next_move"
END_ENDPOINT = "/end_game"


@dataclass
class GameStatus:
    map: list

class Orientation(Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"

class GameHandler:
    logger: Logger

    offense_bot_url: str
    defense_bot_url: str

    map: Map
    offense_player: OffensePlayer | None
    defense_player: DefensePlayer | None
    goal: Position

    def __init__(self, offense_bot_url: str, defense_bot_url: str, logger: Logger) -> None:
        self.logger = logger
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map(random.randint(20, 40), random.randint(20, 40))
        self.goal = self.map.set_goal(self.goal)

        self.offense_player = None
    
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
        response = requests.post(self.defense_bot_url + NEXT_ENDPOINT, json={"map": self.map.to_img_64(self.offense_player.position).decode()})

        # TODO - Preserve the old map

        # TODO - Play the move

        # Validate the move still allows the player to reach the goal
        if not self.map.path_exists(self.offense_player.position, self.goal):
            # TODO - Revert the move
            ...

        # TODO - Update the score
        ...

    def _play_offense(self):
        response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={"map": self.map.to_img_64(self.offense_player.position, 3).decode()})
        data = response.json

        values = [item.value for item in Orientation]
        if data["next_move"] not in values:
            return
        
        previous_offense_position = self.offense_player.position
        
        match(data["next_move"]):
            case "up":
                self.offense_player.position.y += 1
            case "down":
                self.offense_player.position.y -= 1
            case "right":
                self.offense_player.position.x += 1
            case "left":
                self.offense_player.position.x -= 1

        width_map_bounds = self.offense_player.position.x < self.map.width or self.offense_player.position.x > self.map.width
        heigth_map_bounds = self.offense_player.position.y < self.map.height or self.offense_player.position.y > self.map.height

        if width_map_bounds or heigth_map_bounds:
            self.offense_player.position = previous_offense_position

    def get_status(self) -> GameStatus:
        return GameStatus(self.map.to_list())
