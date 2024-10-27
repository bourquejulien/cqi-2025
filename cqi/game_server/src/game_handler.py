from dataclasses import dataclass
import requests
import numpy as np

from logging import Logger

from .map import Map

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

    def __init__(self, offense_bot_url: str, defense_bot_url: str, logger: Logger) -> None:
        self.logger = logger
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        self.map = Map.create_map()
    
    @property
    def is_over(self) -> bool:
        return False

    def play(self):
        requests.post(self.offense_bot_url + START_ENDPOINT,
                      json={"is_offense": True})
        requests.post(self.defense_bot_url + START_ENDPOINT,
                      json={"is_offense": False})

        response1 = requests.post(self.offense_bot_url + NEXT_ENDPOINT, {})
        response2 = requests.post(self.defense_bot_url + NEXT_ENDPOINT, {})

        requests.post(self.offense_bot_url + END_ENDPOINT, {})
        requests.post(self.defense_bot_url + END_ENDPOINT, {})

    def end_game(self):
        ...

    def get_status(self) -> GameStatus:
        return GameStatus(self.map.to_list())
