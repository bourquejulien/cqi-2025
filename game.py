from board import Board
from piece import Piece
from player import Player, Move

class Game:
    board: Board
    real_player: Player
    players: list[Player]
    total_nb_turns: int

    def __init__(self) -> None:
        self.board = Board.simple_board()
        self.real_player = Player(4, "#FFFF00")
        self.players = [Player(1, "#FF0000"), Player(2, "#0000FF"), Player(3, "#00FF00"), self.real_player]

        self.total_nb_turns = 0

    @property
    def current_player(self) -> Player:
        current_player_idx = self.total_nb_turns % len(self.players)
        return self.players[current_player_idx]
    
    @property
    def game_over(self) -> bool:
        return not self.real_player.playing or any([len(player.pieces) == 0 for player in self.players]) or all([not player.playing for player in self.players])
    
    @property
    def first_turn(self) -> bool:
        return self.total_nb_turns < len(self.players)

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

    def to_img_64(self) -> bytes:
        color_mapping = {player.id:player.color for player in self.players}
        color_mapping[0] = "#000000"
        return self.board.to_img_64(color_mapping)
