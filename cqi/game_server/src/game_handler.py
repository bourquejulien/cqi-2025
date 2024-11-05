from dataclasses import dataclass
import requests
import random
import logging

from game_server_common.base import OffenseMove
from .map import Map, Position, ElementType
from .offense_player import OffensePlayer
from .defense_player import DefensePlayer, DefenseMove

START_ENDPOINT = "/start"
NEXT_ENDPOINT = "/next_move"
END_ENDPOINT = "/end_game"
N_WALLS = 20
MAX_MOVES = 100


@dataclass
class GameStatus:
    map: list


class GameHandler:
    offense_bot_url: str
    defense_bot_url: str

    map: Map
    offense_player: OffensePlayer | None
    defense_player: DefensePlayer | None
    goal: Position
    move_count: int

    def __init__(self, offense_bot_url: str, defense_bot_url: str) -> None:
        self.offense_bot_url = offense_bot_url
        self.defense_bot_url = defense_bot_url

        #self.map = Map.create_map(5, 5)
        self.map = Map.create_map(random.randint(20, 40), random.randint(20, 40))
        self.goal = self.map.set_goal()

        self.offense_player = None
        self.defense_player = None
        self.move_count = MAX_MOVES

    @property
    def is_started(self) -> bool:
        return self.offense_player is not None and self.defense_player is not None

    @property
    def is_over(self) -> bool:
        if self.goal is None or self.offense_player is None:
            return False
        
        if self.move_count <= 0:
            return True
        
        return self.goal == self.offense_player.position

    def play(self):
        self._play_defense()
        self._play_offense()

        logging.info(self.map.to_img_64(Position(0, 0)).decode())

    def end_game(self):
        requests.post(self.offense_bot_url + END_ENDPOINT, {})
        requests.post(self.defense_bot_url + END_ENDPOINT, {})

    def start_game(self):
        self.offense_player = OffensePlayer(self.map)
        self.defense_player = DefensePlayer(self.map, n_walls=N_WALLS)

        logging.info("start_game")

        requests.post(self.offense_bot_url + START_ENDPOINT,
                      json={"is_offense": True})
        requests.post(self.defense_bot_url + START_ENDPOINT,
                      json={"is_offense": False, "n_walls": N_WALLS})

    def _play_defense(self):
        response: requests.Response = requests.post(self.defense_bot_url + NEXT_ENDPOINT, json={
                                                    "map": self.map.to_img_64(self.offense_player.position).decode()})

        try:
            response_json = response.json()

            x = response_json["x"]
            assert isinstance(x, int)

            y = response_json["y"]
            assert isinstance(y, int)

            if response_json["element"] == "WALL":
                element = ElementType.WALL
            else:
                logging.info(
                    f"Defense bot returned invalid element: {response_json["element"]}")
                return

            move = DefenseMove(Position(x, y), element)

        except Exception as e:
            logging.error(f"Error parsing response from defense bot: {e}\n{response}")
            return

        self.defense_player.move(move=move,
                                 player=self.offense_player.position,
                                 goal=self.goal)

    def _play_offense(self):
        response = requests.post(self.offense_bot_url + NEXT_ENDPOINT, json={
                                 "map": self.map.to_img_64(self.offense_player.position, 3).decode()})
        
        self.move_count -= 1
        logging.info(f"Remaining number of moves: {self.move_count}")

        move: OffenseMove
        try:
            data = response.json()
            move = OffenseMove(data["move"])
        except Exception as e:
            logging.error(f"Error parsing response from offense bot: {e}")
            return

        if self.move_count <= 0:
            logging.info("No more move available")
            return

        offset = move.to_position()
        previous_offense_position = self.offense_player.position
        self.offense_player.position = self.offense_player.position + offset

        next_tile = self.map.get(self.offense_player.position.x, self.offense_player.position.y)

        if next_tile is None:
            logging.info(f"Offense move out of bounds: {self.offense_player.position} map is {self.map.width}x{self.map.height}")
            self.offense_player.position = previous_offense_position
            return
        
        if next_tile.element not in [ElementType.BACKGROUND, ElementType.GOAL]:
            logging.info(f"Offense move not on a valid map element: {self.offense_player.position} is a {next_tile}")
            self.offense_player.position = previous_offense_position
            return
        
        logging.info(f"Previous offense position: {previous_offense_position}")
        logging.info(f"Goal position: {self.goal}")
        
        logging.info("Offense move valid")
        self.map.set(previous_offense_position.x, previous_offense_position.y, ElementType.BACKGROUND)
        self.map.set(self.offense_player.position.x, self.offense_player.position.y, ElementType.PLAYER_OFFENSE)
        logging.info(f"Offense new position is: {self.offense_player.position}")

    def get_status(self) -> GameStatus:
        return GameStatus(self.map.to_list())
