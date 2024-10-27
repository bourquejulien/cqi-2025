from dataclasses import dataclass
import requests
import random
import numpy as np

from logging import Logger

from .map import Map
from .offense_player import OffensePlayer

START_ENDPOINT = "/start"
NEXT_ENDPOINT = "/next_move"
END_ENDPOINT = "/end_game"


@dataclass
class GameStatus:
    map: list

class GameHandler:
    logger: Logger

    offense_bot_url: str
    defense_bot_url: str

    map: Map
    offense_player: OffensePlayer | None

    def __init__(self, offense_bot_url: str, defense_bot_url: str, logger: Logger) -> None:
        self.logger = logger
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map(random.randint(20, 40), random.randint(20, 40))
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
        requests.post(self.offense_bot_url + START_ENDPOINT,
                json={"is_offense": True})
        requests.post(self.defense_bot_url + START_ENDPOINT,
                      json={"is_offense": False})

    
    def _play_defense(self):
        response = requests.post(self.defense_bot_url + NEXT_ENDPOINT, json={"map": self.map.to_img_64(self.offense_player.position).decode()})
    
    def _play_offense(self):
        response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={"map": self.map.to_img_64(self.offense_player.position, 3).decode()})


    def get_status(self) -> GameStatus:
        return GameStatus(self.map.to_list())
