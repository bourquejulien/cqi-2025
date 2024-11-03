from dataclasses import dataclass
from logging import Logger

from .map import Map, Position, ElementType
@dataclass
class DefenseMove:
    position: Position
    element: ElementType

class DefensePlayer:
    map: Map
    n_walls: int

    def __init__(self, map: Map, n_walls: int = 10) -> None:
        self.map = map
        self.n_walls = n_walls

    def move(self, logger: Logger, move: DefenseMove, player: Position, goal: Position):
        if move.position.x < 0 or move.position.x >= self.map.width or move.position.y < 0 or move.position.y >= self.map.height:
            logger.info(f"Defense move out of bounds: ({move.position.x}, {move.position.y}) map is {self.map.width}x{self.map.height}")
            return
        
        if self.map.map[move.position.x, move.position.y] != ElementType.BACKGROUND:
            logger.info(f"Defense move to non-background: ({move.position.x}, {move.position.y}) is a {self.map.map[move.position.x, move.position.y]}")
            return
        
        if move.element == ElementType.WALL and self.n_walls <= 0:
            logger.info(f"Defense move of wall to ({move.position.x}, {move.position.y}) with no walls left")
            return
        
        self.map.map[move.position.x, move.position.y] = move.element.value

        if not self.map.path_exists(player, goal):
            logger.info(f"Defense move of {self.map.map[move.position.x, move.position.y]} to ({move.position.x}, {move.position.y}) causes no path from player to goal")
            self.map.map[move.position.x, move.position.y] = ElementType.BACKGROUND.value
    
        self.n_walls -= 1