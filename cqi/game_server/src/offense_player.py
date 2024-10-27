from dataclasses import dataclass
import random
import base64

from io import BytesIO
from PIL import Image

from .map import Map, Position

@dataclass
class Move:
    ...

class OffensePlayer:
    map: Map
    position: Position

    def __init__(self, map: Map) -> None:
        self.map = map
        self.position = Position(0, random.randint(0, map.height))
    
    def move(self, move: Move) -> bool:
        ...
    
