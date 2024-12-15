from dataclasses import asdict
import logging
import requests

from interfaces import GameResult, Match

class MainServerClient:
    secret: str
    base_url: str

    def __init__(self, secret: str, base_url: str):
        self.secret = secret
        self.base_url = base_url + "/internal/match"
    
    @property
    def _headers(self) -> str:
        return {"Authorization": f"{self.secret}"}

    def get_next_matches(self, n: int = 1) -> list[Match]:
        logging.info("Getting next %s games", n)

        response: requests.Response
        try:
            response = requests.post(f"{self.base_url}/pop", headers=self._headers, params={"n": n})
        except:
            logging.error("Failed to get next game")
            return []

        if not response.ok:
            logging.error("Failed to get next game")
            return []
        
        matches_data = response.json()
        matches = [Match(**match) for match in matches_data]

        logging.info("Got %s matches", len(matches))
        return matches

    def add_result(self, result: GameResult):
        logging.info("Adding result for match %s", result.id)

        response: requests.Response
        try:
            response = requests.post(f"{self.base_url}/add_result", headers=self._headers, json=asdict(result))
        except:
            logging.error("Failed to add result")
            return

        if not response.ok:
            logging.error("Failed to add result")
