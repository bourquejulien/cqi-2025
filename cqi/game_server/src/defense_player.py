from dataclasses import dataclass

from .map import Map, Position

@dataclass
class Move:
    ...

class DefensePlayer:
    map: Map
    walls: list[Position]

    def __init__(self, map: Map) -> None:
        self.map = map
        self.walls = []
    
    def move(self, move: Move) -> bool:
        ...
    
