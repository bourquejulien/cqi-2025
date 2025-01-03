import math

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Self


@dataclass(eq=True, frozen=True)
class Position:
    x: int
    y: int

    def to(self, other: Self):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: Self):
        return Position(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Self):
        return Position(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y


class DefenseMove(Enum):
    WALL = "wall"
    SKIP = "skip"


class OffenseMove(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    SKIP = "skip"

    def to_position(move: Self) -> Position | None:
        match(move):
            case OffenseMove.UP:
                return Position(0, -1)
            case OffenseMove.DOWN:
                return Position(0, 1)
            case OffenseMove.RIGHT:
                return Position(1, 0)
            case OffenseMove.LEFT:
                return Position(-1, 0)
            case OffenseMove.SKIP:
                return None


class ElementType(Enum):
    UNKNOW = -2
    VISITED = -1
    BACKGROUND = 0
    WALL = 1
    PLAYER_OFFENSE = 2
    GOAL = 3
    LARGE_VISION = 4

    def to_color(self) -> str:
        return ELEMENT_TYPE_TO_COLOR[self]


ELEMENT_TYPE_TO_COLOR = {
    ElementType.UNKNOW: "#DFDFDF",
    ElementType.BACKGROUND: "#FFFFFF",
    ElementType.WALL: "#000000",
    ElementType.PLAYER_OFFENSE: "#FF0000",
    ElementType.GOAL: "#FFD700",
    ElementType.LARGE_VISION: "#4CBB17"
}
