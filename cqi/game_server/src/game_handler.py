import requests
import numpy as np

from logging import Logger

from .map import Map

START_ENDPOINT = "/start"
OFFENSE_ENDPOINT = "/offense"
DEFENSE_ENDPOINT = "/defense"
END_ENDPOINT = "/end_game"


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

    def play(self):
        requests.post(self.offense_bot_url + START_ENDPOINT,
                      json={"is_offense": True})
        requests.post(self.defense_bot_url + START_ENDPOINT,
                      json={"is_offense": False})

        response1 = requests.post(self.offense_bot_url + OFFENSE_ENDPOINT, {})
        response2 = requests.post(self.defense_bot_url + DEFENSE_ENDPOINT, {})

        requests.post(self.offense_bot_url + END_ENDPOINT, {})
        requests.post(self.defense_bot_url + END_ENDPOINT, {})

    def force_end_game(self):
        ...

    def get_status(self) -> dict:
        return {"map": repr(self.map)}
