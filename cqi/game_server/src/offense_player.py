import random

from game_server_common.base import ElementType

from .map import Map, Position

OFFENSE_VISION_RADIUS = 3
FULL_VISION_RADIUS = 1_000_000

class OffensePlayer:
    map: Map
    position: Position

    def __init__(self, map: Map) -> None:
        self.map = map
        self.position = Position(0, random.randint(0, map.height - 1))
        self.map.set(self.position.x, self.position.y, ElementType.PLAYER_OFFENSE)
    
    def get_vision_radius(self) -> int:
        return FULL_VISION_RADIUS if self.map.get(*self.position).element == ElementType.LARGE_VISION else OFFENSE_VISION_RADIUS
