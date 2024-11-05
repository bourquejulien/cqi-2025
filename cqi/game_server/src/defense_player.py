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

    def __init__(self, map: Map, n_walls: int) -> None:
        self.map = map
        self.n_walls = n_walls

    def move(self, move: DefenseMove, player: Position, goal: Position):
        tile = self.map.get(move.position.x, move.position.y)
        if tile is None:
            logging.info(f"Defense move out of bounds: {move.position} map is {self.map.width}x{self.map.height}")
            return
        
        if tile.element != ElementType.BACKGROUND:
            logging.info(f"Defense move to non-background: {move.position} is a {tile}")
            return
        
        if move.element == ElementType.WALL and self.n_walls <= 0:
            logging.info(f"Defense move of wall to {move.position} with no walls left")
            return
        
        self.map.set(move.position.x, move.position.y, move.element)

        if not self.map.path_exists(player, goal):
            logging.info(f"Defense move of {tile} to {move.position} causes no path from player to goal")
            self.map.set(move.position.x, move.position.y, ElementType.BACKGROUND)  

        logging.info("Defense move valid")
        self.n_walls -= 1
