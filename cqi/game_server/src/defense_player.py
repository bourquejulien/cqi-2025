from dataclasses import dataclass

from .map import Map, Position, ElementType
from .timebomb import Timebomb
from .logger import Level, Logger

@dataclass
class DefenseMove:
    position: Position
    element: ElementType

class DefensePlayer:
    map: Map
    timebomb: Timebomb
    logger: Logger

    n_walls: int

    def __init__(self, map: Map, timebomb: Timebomb, logger: Logger, n_walls: int) -> None:
        self.map = map
        self.timebomb = timebomb
        self.logger = logger

        self.n_walls = n_walls

    def move(self, move: DefenseMove, player_position: Position) -> bool:
        tile = self.map.get(move.position.x, move.position.y)
        if tile is None:
            self.logger.add(f"Defense move out of bounds: {move.position}, the map is {self.map.width}x{self.map.height}", Level.INFO)
            return False
        
        if tile.element != ElementType.BACKGROUND:
            self.logger.add(f"Defense move to non-background: {move.position} is a {tile}", Level.INFO)
            return False
        
        if move.element == ElementType.WALL and self.n_walls <= 0:
            self.logger.add(f"Defense move of wall to {move.position} with no walls left", Level.INFO)
            return False
        
        if move.element == ElementType.TIMEBOMB:
            return self.timebomb.drop(move.position, player_position)
        
        self.map.set(move.position.x, move.position.y, move.element)

        if not self.map.path_exists(player_position):
            self.logger.add(f"Defense move of {tile} to {move.position} causes no path from player to goal", Level.INFO)
            self.map.set(move.position.x, move.position.y, ElementType.BACKGROUND)

        self.logger.add(f"Wall placed at: {move.position}", Level.INFO)
        self.n_walls -= 1

        return True
