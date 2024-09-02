import PIL.Image
import numpy as np
import PIL
from piece import Piece

TILE_SIZE = 20

class Board:
    def __init__(self, board: np.ndarray):
        self.board: np.ndarray = board
        self.width = board.shape[0]
        self.height = board.shape[1]

    def add_piece(self, piece: Piece, orientation: Piece.Orientation, x: int, y: int, first_piece: bool) -> bool:
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
        
        # Ajouter la pièce
        if valid_placement:
            for i in range(piece.size):
                for j in range(piece.size):
                    if shape[i][j] != 1:
                        self.board[x + i][y + j] = shape[i][j]
                    
        return valid_placement                   
    
    def __str__(self):
        return str(self.board)
    
    def to_img(self) -> list[bytes]:
        # Create an image of the board
        img = PIL.Image.new('RGB', (self.width * TILE_SIZE, self.height * TILE_SIZE), color = 'black')

        for i in range(self.width):
            for j in range(self.height):
                if self.board[i][j] == 0:
                    img.paste('black', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif self.board[i][j] == 1:
                    img.paste('red', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif self.board[i][j] == 2:
                    img.paste('blue', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif self.board[i][j] == 3:
                    img.paste('green', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))
                elif self.board[i][j] == 4:
                    img.paste('yellow', (i * TILE_SIZE, j * TILE_SIZE, (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE))

        with open('board.png', 'wb') as f:
            img.save(f, 'PNG')
            
        return img.tobytes()

    @classmethod
    def simple_board(cls, width = 20, height = 20):
        return cls(np.array([[0] * width] * height))
    

    