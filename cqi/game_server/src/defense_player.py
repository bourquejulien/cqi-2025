from dataclasses import dataclass
import logging

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

    def move(self, move: DefenseMove, player: Position, goal: Position):
        if move.position.x < 0 or move.position.x >= self.map.width or move.position.y < 0 or move.position.y >= self.map.height:
            logging.info(f"Defense move out of bounds: ({move.position.x}, {move.position.y}) map is {self.map.width}x{self.map.height}")
            return
        
        if self.map.map[move.position.x, move.position.y] != ElementType.BACKGROUND.value:
            logging.info(f"Defense move to non-background: ({move.position.x}, {move.position.y}) is a {self.map.map[move.position.x, move.position.y]}")
            return
        
        if move.element == ElementType.WALL.value and self.n_walls <= 0:
            logging.info(f"Defense move of wall to ({move.position.x}, {move.position.y}) with no walls left")
            return
        
        self.map.map[move.position.x, move.position.y] = move.element.value

        logging.info("Validating that path to goal exists")
        if not self.map.path_exists(player, goal):
            logging.info(f"Defense move of {self.map.map[move.position.x, move.position.y]} to ({move.position.x}, {move.position.y}) causes no path from player to goal")
            self.map.map[move.position.x, move.position.y] = ElementType.BACKGROUND.value

        logging.info("Defense move valid")
        self.n_walls -= 1