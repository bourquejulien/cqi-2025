from dataclasses import dataclass
import PIL.Image
import numpy as np
import PIL
from enum import Enum
from typing import Self

from .piece_shapes import PIECE_SHAPES

TILE_SIZE = 20

class Piece:
    id: int
    size: int
    shape: np.ndarray
    value: int

    class Orientation(Enum):
        UP = "up"
        RIGHT = "right"
        DOWN = "down"
        LEFT = "left"
        
    # A piece is a square shape filled with 1s and 0s
    # The 1s represent the piece and the 0s represent the empty space
    # The piece has a direction describing its rotation
    # The piece has a size describing its width and height
    # Each shape must have a unique id
    # Player id are 1, 2, 3, 4
    # Piece id are from 1 to 99
    def __init__(self, shape: np.ndarray, player_id: int, piece_id: int):
        # Setup the shape with the id
        self.id = piece_id

        self.shape = shape.copy()
        self.shape[self.shape == 1] = player_id

        # Get the size
        self.size = self.shape.shape[0]

        self.value = sum([1 for segment in self.shape.flat if segment == player_id])

    def get_shape(self, orientation: Orientation) -> np.ndarray:
        k = {
            Piece.Orientation.UP: 0,
            Piece.Orientation.RIGHT: 1,
            Piece.Orientation.DOWN: 2,
            Piece.Orientation.LEFT: 3
        }.get(orientation)
        return np.rot90(self.shape, k)
    
    def to_img(self, orientation: Orientation, color: str) -> PIL.Image:
        img = PIL.Image.new("RGB", (self.size * TILE_SIZE, self.size * TILE_SIZE), color = "black")

        shape = self.get_shape(orientation)

        for i in range(self.size):
            for j in range(self.size):
                if shape[i][j] == 0:
                    img.paste("#000000", (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                else:
                    img.paste(color, (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
            
        return img

@dataclass
class PieceWithMetadata:
    piece: Piece
    count: int

    def summary(self) -> dict:
        return {
            "id": self.piece.id,
            "count": self.count,
            "shape": self.piece.shape.tolist()
        }

    @classmethod
    def create_pieces(cls, player_id: int) -> list[Self]:
        return [cls(Piece(piece_data["piece"], player_id, piece_id), piece_data["count"]) for piece_id, piece_data in enumerate(PIECE_SHAPES)]
