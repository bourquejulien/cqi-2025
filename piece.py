import numpy as np
import PIL
from enum import Enum

TILE_SIZE = 20

class Piece:
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

    def get_shape(self, orientation: Orientation) -> np.ndarray:
        def k():
            match orientation:
                case Piece.Orientation.UP:
                    return 0
                case Piece.Orientation.RIGHT:
                    return 1
                case Piece.Orientation.DOWN:
                    return 2
                case Piece.Orientation.LEFT:
                    return 3
        return np.rot90(self.shape, k())
    
    def to_img(self, orientation: Orientation, name="piece") -> bytes:
        # Create an image of the board
        img = PIL.Image.new('RGB', (self.size * TILE_SIZE, self.size * TILE_SIZE), color = 'black')

        shape = self.get_shape(orientation)

        for i in range(self.size):
            for j in range(self.size):
                if shape[i][j] == 0:
                    img.paste('black', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif shape[i][j] == 1:
                    img.paste('red', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif shape[i][j] == 2:
                    img.paste('blue', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif shape[i][j] == 3:
                    img.paste('green', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif shape[i][j] == 4:
                    img.paste('yellow', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))

        with open(f"{name}.png", 'wb') as f:
            img.save(f, 'PNG')
            
        return img.tobytes()
        
    
# ID of the piece is the index of the shape in the list
PIECE_SHAPES = [
    np.array(
        [[1]]
    ),
    np.array(
        [[1, 0],
         [1, 0]]
    ),
    np.array(
        [[1, 0],
         [1, 1]]
    ),
    np.array(
        [[1, 0, 0],
         [1, 0, 0],
         [1, 0, 0]]
    ),
    np.array(
        [[1, 0, 0, 0],
         [1, 0, 0, 0],
         [1, 0, 0, 0],
         [1, 0, 0, 0]]
    ),
    np.array(
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ),
    np.array(
        [[1, 0, 0],
         [1, 1, 0],
         [1, 0, 0]]
    ),
    np.array(
        [[1, 1],
         [1, 1]]
    ),
    np.array(
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]]
    ),
    np.array(
        [[1, 0, 0, 0, 0],
         [1, 0, 0, 0, 0],
         [1, 0, 0, 0, 0],
         [1, 0, 0, 0, 0],
         [1, 0, 0, 0, 0]]
    ),
    np.array(
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [1, 1, 0, 0]]
    ),
    np.array(
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [1, 1, 0, 0],
         [1, 0, 0, 0]]
    ),
    np.array(
        [[0, 1, 0],
         [1, 1, 0],
         [1, 1, 0]]
    ),
    np.array(
        [[1, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ),
    np.array(
        [[1, 0, 0, 0],
         [1, 1, 0, 0],
         [1, 0, 0, 0],
         [1, 0, 0, 0]]
    ),
    np.array(
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 1]]
    ),
    np.array(
        [[1, 0, 0],
         [1, 0, 0],
         [1, 1, 1]]
    ),
    np.array(
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ),
    np.array(
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 1]]
    ),
    np.array(
        [[1, 0, 0],
         [1, 1, 1], 
         [0, 1, 0]]
    ),
    np.array(
        [[0, 1, 0],
         [1, 1, 1],
         [0, 1, 0]]
    )
]
