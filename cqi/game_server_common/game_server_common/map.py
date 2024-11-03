from enum import Enum
from typing import Self
import numpy as np

from dataclasses import dataclass
from .base import OffenseMove, Position

@dataclass(eq=True, frozen=True)
class Tile:
    position: Position
    id: int

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
        return self.position.y

class Map:
    map: np.ndarray
    def __init__(self, map: np.ndarray) -> None:
        self.map = map

    def get(self, x: int, y: int)-> Tile | None:
        size_x, size_y = self.map.shape
        if 0 <= x < size_x and 0 <= y < size_y:
            return Tile(Position(x, y), self.map[x, y])
        return None
    
    def get_nearby_tiles(self, x: int, y: int)-> list[tuple[Tile, OffenseMove]]:
        if self.get(x, y) == None:
            return []
        
        tiles: list[Tile | None] = []

        tiles.append((self.get(x - 1, y), OffenseMove.LEFT))
        tiles.append((self.get(x + 1, y), OffenseMove.RIGHT))
        tiles.append((self.get(x, y - 1), OffenseMove.DOWN))
        tiles.append((self.get(x, y + 1), OffenseMove.UP))

        return [(tile, move) for tile, move in tiles if tile is not None]
