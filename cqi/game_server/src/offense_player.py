import random

from game_server_common.base import ElementType, OffenseMove

from .logger import Level, Logger
from .map import Map, Position

OFFENSE_VISION_RADIUS = 3
FULL_VISION_RADIUS = 1_000_000

class OffensePlayer:
    map: Map
    logger: Logger

    position: Position
    is_large_vision: bool

    def __init__(self, map: Map, logger: Logger) -> None:
        self.map = map
        self.logger = logger

        self.position = Position(0, random.randint(0, map.height - 1))
        self.map.set(self.position.x, self.position.y, ElementType.PLAYER_OFFENSE)
        self.is_large_vision = False
    
    def get_vision_radius(self) -> int:
        if self.is_large_vision:
            return FULL_VISION_RADIUS
        
        return OFFENSE_VISION_RADIUS
    
    def get_and_remove_vision_radius(self) -> int:
        radius = self.get_vision_radius()
        self.is_large_vision = False
        return radius
    
    def move(self, move: OffenseMove):
        if move == OffenseMove.SKIP:
            self.logger.add(f"Offense move skipped", Level.INFO)
            return

        offset = move.to_position()
        new_position = self.position + offset

        next_tile = self.map.get(new_position.x, new_position.y)

        if next_tile is None:
            self.logger.add(f"Offense move out of bounds: {new_position}", Level.INFO)
            return

        if next_tile.element not in [ElementType.BACKGROUND, ElementType.GOAL, ElementType.LARGE_VISION]:
            self.logger.add(f"Offense move not on a valid map element: {new_position} is a {next_tile}", Level.INFO)
            return
        
        if next_tile.element == ElementType.LARGE_VISION:
            self.is_large_vision = True
            self.logger.add(f"Large vision enabled on next move", Level.INFO)

        self.logger.add(f"Previous offense position: {self.position}", Level.INFO)
        self.logger.add("Offense move valid", Level.INFO)
        
        self.map.set(self.position.x, self.position.y, ElementType.BACKGROUND)
        self.map.set(new_position.x, new_position.y, ElementType.PLAYER_OFFENSE)
        self.position = new_position

        self.logger.add(f"Offense new position is: {self.position}", Level.DEBUG)
