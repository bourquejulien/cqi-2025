from peice import Peice, PEICE_SHAPES
from board import Board

class Player:
    def __init__(self, id: int, npc: bool = False):
        self.playing = False
        self.id = id
        self.create_peices()
    
    def create_peices(self) -> list[Peice]:
        self.peices = [Peice(shape, self.id, peice_id) for peice_id, shape in enumerate(PEICE_SHAPES)]

    @property
    def peices_remaining(self) -> int:
        return len(self.peices)

    @property
    def score(self) -> int:
        score = 0

        for peice in self.peices:
            for segment in peice.shape.flat:
                if segment == 1:
                    score += 1

        return score

    def play(self, board: Board, peice_id: int, orientation: Peice.Orientation, x: int, y: int, first_peice: bool = False) -> bool:
        peice = self.peices[peice_id]
        sucess = board.add_peice(peice, orientation, x, y, first_peice)
        
        if sucess:
            del self.peices[peice_id]

        return sucess
