from .board import Board
from .player import Player, Move

class Game:
    board: Board
    real_player: Player
    players: list[Player]
    total_nb_turns: int
    is_user_ended: bool

    def __init__(self, real_player_idx: int) -> None:
        self.board = Board.simple_board()
        self.players = [Player(1, "#FF0000"), Player(2, "#0000FF"), Player(3, "#00FF00"), Player(4, "#FFFF00")]

        self.real_player = self.players[real_player_idx]
        self.total_nb_turns = 0
        self.is_user_ended = False

    @property
    def current_player(self) -> Player:
        current_player_idx = self.total_nb_turns % len(self.players)
        return self.players[current_player_idx]
    
    @property
    def game_over(self) -> bool:
        return self.is_user_ended or not self.real_player.playing or any([len(player.pieces) == 0 for player in self.players]) or all([not player.playing for player in self.players])
    
    def play_move(self, move: Move) -> None:
        # Get the player playing
        player = self.current_player
        
        # If the player is not playing skip him
        if not player.playing:
            return
        
        # Play the move
        player.play(board=self.board, move=move)

        # Increment the number of turns played
        self.total_nb_turns += 1

    def force_end_game(self):
        self.is_user_ended = True

    def to_img_64(self) -> bytes:
        color_mapping = {player.id:player.color for player in self.players}
        color_mapping[0] = "#000000"
        return self.board.to_img_64(color_mapping)
