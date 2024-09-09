from board import Board
from piece import Piece
from player import Player, Move

class Game:
    board: Board
    players: list[Player]
    real_player_id: int
    current_player_id: int
    total_nb_turns: int

    def __init__(self) -> None:
        self.board = Board.simple_board()
        self.players = [Player(1), Player(2), Player(3), Player(4)]

        self.real_player_id = 3
        self.current_player_id = 0
        self.total_nb_turns = 0

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_id]
    
    @property
    def real_player(self) -> Player:
        return self.players[self.real_player_id]
    
    @property
    def game_over(self) -> bool:
        return not self.players[self.real_player_id].playing or any([len(player.pieces) == 0 for player in self.players]) or all([not player.playing for player in self.players])
    
    @property
    def first_turn(self) -> bool:
        return self.total_nb_turns < len(self.players)

    def next_turn(self):
        # Go to the next player
        self.current_player_id = (self.current_player_id + 1) % len(self.players)

    def play_turn(self, x: int, y: int, orientation: Piece.Orientation, piece_id: int) -> None:
        self.play_move(Move(x, y, orientation, piece_id))

    def play_move(self, move: Move) -> None:
        # Get the player playing
        player = self.current_player
        
        # If the player is not playing skip him
        if not player.playing:
            return
        
        # Play the move
        player.playing = player.play(board=self.board, move=move, first_piece=self.first_turn)

        # Increment the number of turns played
        self.total_nb_turns += 1
