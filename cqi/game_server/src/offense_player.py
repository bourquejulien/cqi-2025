import random

from logger import Level, Logger
from game_server_common.base import ElementType, OffenseMove

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
            self.is_large_vision = False
            return FULL_VISION_RADIUS
        
        return OFFENSE_VISION_RADIUS
    
    def move(self, move: OffenseMove):
        offset = move.to_position()
        new_position = self.position + offset

        next_tile = self.map.get(new_position.x, new_position.y)

        if next_tile is None:
            self.logger.add(f"Offense move out of bounds: {new_position}", Level.INFO)
            return

        if next_tile.element not in [ElementType.BACKGROUND, ElementType.GOAL, ElementType.LARGE_VISION]:
            self.logger.add(f"Offense move not on a valid map element: {new_position} is a {next_tile.element}", Level.INFO)
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

        # match self.timebomb_countdown:
        #     case 2:
        #         self.timebomb_countdown -= 1
        #         self.map.set(self.timebomb.x, self.timebomb.y, ElementType.TIMEBOMB_SECOND_ROUND)
        #     case 1:
        #         self.timebomb_countdown -= 1
        #         self.map.set(self.timebomb.x, self.timebomb.y, ElementType.TIMEBOMB_THIRD_ROUND)
        #     case 0:
        #         self.map.set(self.timebomb.x, self.timebomb.y, ElementType.BACKGROUND)
        #         radius = abs(self.offense_player.position.x - self.timebomb.x) <= 1 and abs(self.offense_player.position.y - self.timebomb.y) <= 1
        #         if self.offense_player.position == self.timebomb or (self.timebomb and radius):
        #             self.available_moves = max(0, self.available_moves - 10)
        #             return
