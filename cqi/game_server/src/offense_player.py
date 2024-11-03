from dataclasses import dataclass
import random

from game_server_common.base import ElementType

from .map import Map, Position

class OffensePlayer:
    map: Map
    position: Position

    def __init__(self, map: Map) -> None:
        self.map = map
        self.position = Position(0, random.randint(0, map.height))
        self.map.map[self.position.x, self.position.y] = ElementType.PLAYER_OFFENSE.value
