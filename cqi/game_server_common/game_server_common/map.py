import numpy as np
import base64

TILE_SIZE = 20

from PIL import Image
from io import BytesIO
from dataclasses import dataclass
from .base import ElementType, OffenseMove, Position


@dataclass(eq=True, frozen=True)
class Tile:
    position: Position
    element: ElementType

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
        return self.position.y
    
    def __repr__(self) -> str:
        return self.element.name

class Map:
    map: np.ndarray

    def __init__(self, map: np.ndarray) -> None:
        self.map = map

    def get(self, x: int, y: int) -> Tile | None:
        size_x, size_y = self.map.shape
        if 0 <= x < size_x and 0 <= y < size_y:
            return Tile(Position(x, y), ElementType(self.map[x, y]))
        return None

    def set(self, x: int, y: int, element_type: ElementType) -> bool:
        assert type(element_type) == ElementType

        size_x, size_y = self.map.shape
        if 0 <= x < size_x and 0 <= y < size_y:
            self.map[x, y] = element_type.value
            return True
        return False
    
    def to_img_64(self) -> bytes:
        """Creates a base64 image of the map"""
        image = Image.new("RGB", (self.map.shape[0] * TILE_SIZE, self.map.shape[1] * TILE_SIZE), color = ElementType.BACKGROUND.to_color())

        def img_paste(x :int, y: int, type: ElementType):
            image.paste(type.to_color(), (x * TILE_SIZE, y * TILE_SIZE, (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
        
        for x in range(self.map.shape[0]):
            for y in range(self.map.shape[1]):
                element_type = ElementType(self.map[x, y])
                if element_type is not ElementType.BACKGROUND:
                    img_paste(x, y, element_type)

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    def get_nearby_tiles(self, x: int, y: int) -> list[tuple[Tile, OffenseMove]]:
        if self.get(x, y) is None:
            return []

        tiles: list[Tile | None] = []

        tiles.append((self.get(x - 1, y), OffenseMove.LEFT))
        tiles.append((self.get(x + 1, y), OffenseMove.RIGHT))
        tiles.append((self.get(x, y + 1), OffenseMove.DOWN))
        tiles.append((self.get(x, y - 1), OffenseMove.UP))

        return [(tile, move) for tile, move in tiles if tile is not None]
