import math

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Self


class Move(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@dataclass(eq=True, frozen=True)
class Position:
    x: int
    y: int

    def to(self, other: Self):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y


class ElementType(Enum):
    VISITED = -1
    BACKGROUND = 0
    WALL = 1
    PLAYER_OFFENSE = 2
    GOAL = 3

    def to_color(self) -> str:
        return ELEMENT_TYPE_TO_COLOR[self]


ELEMENT_TYPE_TO_COLOR = {
    ElementType.BACKGROUND: "#FFFFFF",
    ElementType.WALL: "#000000",
    ElementType.PLAYER_OFFENSE: "#FF0000",
    ElementType.GOAL: "#FFD700"
}
