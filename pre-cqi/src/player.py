from dataclasses import dataclass

from .piece import Piece, PieceWithMetadata
from .board import Board

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
    is_first_move: bool
    pieces_with_count: list[PieceWithMetadata]

    def __init__(self, id: int, color: str):
        self.id = id
        self.color = color
        self.playing = True
        self.is_first_move = True
        self.pieces_with_count = PieceWithMetadata.create_pieces(self.id)
    
    @property
    def pieces(self) -> list[Piece]:
        return [data.piece for data in self.pieces_with_count if data.count > 0]

    @property
    def score(self) -> int:
        return sum([data.piece.value * data.count for data in self.pieces_with_count])

    def play(self, board: Board, move: Move):
        chosen_piece: Piece | None = None

        # Get the piece
        for piece in self.pieces:
            if piece.id == move.piece_id:
                chosen_piece = piece
                break
        
        if chosen_piece is None:
            self.playing = False
            return
        
        success = board.add_piece(piece, move.orientation, move.x, move.y, self.is_first_move)
        
        if success:
            self.pieces_with_count[chosen_piece.id].count -= 1

        self.is_first_move = False
        self.playing = success
