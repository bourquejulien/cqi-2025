#!/bin/env python3

from dataclasses import dataclass
from PIL import Image
from io import BytesIO

import numpy as np
import base64

@dataclass
class Tile:
    x: int
    y: int
    id: int

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
    
    def to_img_64(self) -> bytes:
        """Creates a base64 image of the map"""
        image = Image.new("RGB", (self.width, self.height), color = "white")
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @classmethod
    def create_map(cls, width = 20, height = 20):
        return cls(np.array([[0] * width] * height))
