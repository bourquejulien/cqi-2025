from piece import Piece, PIECE_SHAPES
from board import Board

class Player:
    def __init__(self, id: int, npc: bool = False):
        self.playing = True
        self.id = id
        self.create_pieces()
    
    def create_pieces(self) -> list[Piece]:
        self.pieces = [Piece(shape, self.id, piece_id) for piece_id, shape in enumerate(PIECE_SHAPES)]

    @property
    def pieces_remaining(self) -> int:
        return len(self.pieces)

    @property
    def score(self) -> int:
        score = 0

        for piece in self.pieces:
            for segment in piece.shape.flat:
                if segment == self.id:
                    score += 1

        return score

    def play(self, board: Board, piece_id: int, orientation: Piece.Orientation, x: int, y: int, first_piece: bool = False) -> bool:
        # Get the piece
        chosen_piece = None
        for piece in self.pieces:
            if piece.id == piece_id:
                chosen_piece = piece
                break
        
        if chosen_piece is None:
            return False
        
        success = board.add_piece(piece, orientation, x, y, first_piece)
        
        if success:
            self.pieces.remove(chosen_piece)

        return success
