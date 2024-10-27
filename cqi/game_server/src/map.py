#!/bin/env python3

from enum import Enum
from dataclasses import dataclass
from PIL import Image
from io import BytesIO

import numpy as np
import base64

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Tile:
    x: int
    y: int
    id: int

TILE_SIZE = 20

class ElementType(Enum):
    BACKGROUND = 0
    WALL = 1
    PLAYER_OFFENSE = 2

ELEMENT_TYPE_TO_COLOR = {
    ElementType.BACKGROUND: "#FFFFFF",
    ElementType.WALL: "#000000",
    ElementType.PLAYER_OFFENSE: "#FF0000"
}

class Map:
    map: np.ndarray
    width: int
    height: int

    def __init__(self, map: np.ndarray) -> None:
        self.map = map
        self.width = map.shape[0]
        self.height = map.shape[1]

    def __str__(self) -> str:
        return str(self.map)
    
    def __repr__(self) -> str:
        return repr(self.map)
    
    def to_list(self) -> list:
        return self.map.tolist()
    
    def to_img_64(self, offense_position: Position, radius: int = None) -> bytes:
        """Creates a base64 image of the map"""
        image = Image.new("RGB", (self.width * TILE_SIZE, self.height * TILE_SIZE), color = ELEMENT_TYPE_TO_COLOR.get(ElementType.BACKGROUND))

        def img_paste(x :int, y: int, type: ElementType):
            image.paste(ELEMENT_TYPE_TO_COLOR.get(type), (x * TILE_SIZE, y * TILE_SIZE, (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
        
        for x in range(self.width):
            for y in range(self.height):
                element_type = ElementType(self.map[x, y])
                if element_type is not ElementType.BACKGROUND:
                    img_paste(x, y, element_type)

        img_paste(offense_position.x, offense_position.y, ElementType.PLAYER_OFFENSE)

        if radius is not None:
            left = max(0, offense_position.x - radius)
            right = min(self.width, offense_position.x + radius)
            upper = max(0, offense_position.y - radius)
            lower = min(self.height, offense_position.y + radius)
            image = image.crop(tuple([value * TILE_SIZE for value in [left, upper, right, lower]]))

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @classmethod
    def create_map(cls, width: int = 20, height: int = 20):
        return cls(np.array([[ElementType.BACKGROUND.value] * width] * height))
