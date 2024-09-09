from dataclasses import dataclass
from piece import Piece
from piece_shapes import PIECE_SHAPES
from board import Board

@dataclass
class Move:
    x: int
    y: int
    orientation: Piece.Orientation
    piece_id: int
    
    @classmethod
    def from_request(cls, x: int, y: int, orientation: str, piece_id: int):
        return cls(x, y, Piece.Orientation(orientation.lower()), piece_id)

class Player:
    id: int
    color: str
    playing: bool
    pieces: list[Piece]

    def __init__(self, id: int, color: str):
        self.id = id
        self.color = color
        self.playing = True
        self.create_pieces()
    
    def create_pieces(self) -> list[Piece]:
        self.pieces = [Piece(shape, self.id, piece_id) for piece_id, shape in enumerate(PIECE_SHAPES)]

    @property
    def pieces_remaining(self) -> int:
        return len(self.pieces)

    @property
    def score(self) -> int:
        return sum([piece.value for piece in self.pieces])

    def play(self, board: Board, move: Move, first_piece: bool = False) -> bool:
        chosen_piece: Piece | None = None

        # Get the piece
        for piece in self.pieces:
            if piece.id == move.piece_id:
                chosen_piece = piece
                break
        
        if chosen_piece is None:
            return False
        
        success = board.add_piece(piece, move.orientation, move.x, move.y, first_piece)
        
        if success:
            self.pieces.remove(chosen_piece)

        return success
