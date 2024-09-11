from collections import deque
from dataclasses import dataclass
from io import BytesIO
import PIL.Image
import numpy as np
import PIL
import base64

from .piece import Piece

TILE_SIZE = 20

@dataclass(eq=True, frozen=True)
class Tile:
    x: int
    y: int
    id: int

class Board:
    board: np.ndarray
    width: int
    height: int

    def __init__(self, board: np.ndarray):
        self.board = board
        self.width = board.shape[0]
        self.height = board.shape[1]

    @property
    def is_empty(self) -> bool:
        return not self.board.any()

    def get(self, x: int, y: int)-> Tile | None:
        size_x, size_y = self.board.shape
        if 0 <= x < size_x and 0 <= y < size_y:
            return Tile(x, y, self.board[x, y])
        return None
    
    def get_nearby_tiles(self, x: int, y: int)-> list[Tile]:
        if self.get(x, y) == None:
            return []
        
        tiles: list[Tile | None] = []

        tiles.append(self.get(x - 1, y))
        tiles.append(self.get(x + 1, y))
        tiles.append(self.get(x, y - 1))
        tiles.append(self.get(x, y + 1))

        return [tile for tile in tiles if tile is not None]
    
    # Get nearest tile from a give location
    def get_nearest_tile(self, x: int, y: int) -> Tile | None:
        first_tile = self.get(x, y)

        if first_tile is None:
            return None

        visited: set[Tile] = set()
        to_visit: deque[Tile] = deque([first_tile])

        while len(to_visit) > 0:
            current = to_visit.pop()

            if(current.id != 0):
                return current

            visited.add(current)
            to_visit.extend([tile for tile in self.get_nearby_tiles(current.x, current.y) if not tile in visited])
        
        return None

    def add_piece(self, piece: Piece, orientation: Piece.Orientation, x: int, y: int, first_piece: bool) -> bool:
        shape: np.ndarray = piece.get_shape(orientation)

        if not self.check_piece(piece, orientation, x, y, first_piece):
            return False
        
        # Ajouter la pièce
        for i in range(piece.size):
            for j in range(piece.size):
                if shape[i][j] != 0:
                    self.board[x + i][y + j] = shape[i][j]
                    
        return True 

    def check_piece(self, piece: Piece, orientation: Piece.Orientation, x: int, y: int, first_piece: bool) -> bool:
        shape: np.ndarray = piece.get_shape(orientation)
        
        valid_placement = False

        # Verifier si le placement est valide
        for i in range(piece.size):
            for j in range(piece.size):
                if shape[i][j] != 0:
                    
                    # Part of the piece is off the board
                    if x + i >= self.width or y + j >= self.height:
                        return False
                    if x + i < 0 or y + j < 0:
                        return False
                    
                    # Check if the piece overlaps with the board or another piece
                    if self.board[x + i][y + j] != 0:
                        return False
                    
                    # Check if the piece touches directly a piece of the same color right
                    if x + i + 1 < self.width:
                        if self.board[x + i + 1][y + j] == shape[i][j]:
                            return False
                    elif first_piece:
                        valid_placement = True

                    # Check if the piece touches directly a piece of the same color left
                    if x + i - 1 >= 0:
                        if self.board[x + i - 1][y + j] == shape[i][j]:
                            return False
                    elif first_piece:
                        valid_placement = True

                    # Check if the piece touches directly a piece of the same color down
                    if y + j + 1 < self.height:
                        if self.board[x + i][y + j + 1] == shape[i][j]:
                            return False
                    elif first_piece:
                        valid_placement = True

                    # Check if the piece touches directly a piece of the same color up
                    if y + j - 1 >= 0:
                        if self.board[x + i][y + j - 1] == shape[i][j]:
                            return False
                    elif first_piece:
                        valid_placement = True
                    
                    if not valid_placement:
                        if x + i + 1 < self.width and y + j + 1 < self.height:
                            if self.board[x + i + 1][y + j + 1] == shape[i][j]:
                                valid_placement = True

                        if x + i + 1 < self.width and y + j - 1 >= 0:
                            if self.board[x + i + 1][y + j - 1] == shape[i][j]:
                                valid_placement = True
                        
                        if x + i - 1 >= 0 and y + j + 1 < self.height:
                            if self.board[x + i - 1][y + j + 1] == shape[i][j]:
                                valid_placement = True
                        
                        if x + i - 1 >= 0 and y + j - 1 >= 0:
                            if self.board[x + i - 1][y + j - 1] == shape[i][j]:
                                valid_placement = True
        
        return valid_placement
                        
    def __str__(self):
        return str(self.board)
    
    def to_img_64(self, color_mapping: dict) -> bytes:
        # Create an image of the board
        img = PIL.Image.new("RGB", (self.width * TILE_SIZE, self.height * TILE_SIZE), color = "black")

        for i in range(self.width):
            for j in range(self.height):
                color = color_mapping[int(self.board[i][j])]
                img.paste(color, (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
       
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @classmethod
    def simple_board(cls, width = 20, height = 20):
        return cls(np.array([[0] * width] * height))
