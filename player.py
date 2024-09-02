from piece import Piece, PEICE_SHAPES
from board import Board

class Player:
    def __init__(self, id: int, npc: bool = False):
        self.playing = False
        self.id = id
        self.create_pieces()
    
    def create_pieces(self) -> list[Piece]:
        self.pieces = [Piece(shape, self.id, piece_id) for piece_id, shape in enumerate(PEICE_SHAPES)]

    @property
    def pieces_remaining(self) -> int:
        return len(self.pieces)

    @property
    def score(self) -> int:
        score = 0

        for piece in self.pieces:
            for segment in piece.shape.flat:
                if segment == 1:
                    score += 1

        return score

    def play(self, board: Board, piece_id: int, orientation: Piece.Orientation, x: int, y: int, first_piece: bool = False) -> bool:
        piece = self.pieces[piece_id]
        sucess = board.add_piece(piece, orientation, x, y, first_piece)
        
        if sucess:
            del self.pieces[piece_id]

        return sucess
