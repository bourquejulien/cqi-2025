from board import Board
from piece import Piece
from player import Player
import random

class Game:
    def __init__(self) -> None:
        self.game_over = False
        self.board = Board.simple_board()
        self.players = [Player(1), Player(2), Player(3), Player(4)]

        self.real_player_id = 3
        self.player_playing = 0
        self.first_turn = True
        self.total_nb_turns = 0

    def setup_turn(self):
        # Check if the game is over (All players are not playing)
        if not any([player.playing for player in self.players]):
            self.game_over = True

        # Check if the current player has no more pieces to play
        if len(self.players[self.player_playing].pieces) == 0:
            self.game_over = True

        # Check if we are at still the first turn
        if self.total_nb_turns >= len(self.players):
            self.first_turn = False

        # Go to the next player
        self.player_playing = (self.player_playing + 1) % len(self.players)

    def play_turn(self, x: int, y: int, orientation: Piece.Orientation, piece_id: int) -> None:
        # Increment the number of turns played
        self.total_nb_turns += 1

        # Get the player playing
        player = self.players[self.player_playing]
        
        # If the player is not playing skip him
        if not player.playing:
            return
        
        # Play the move
        player.playing = player.play(
            board=self.board,
            piece_id=piece_id, 
            orientation=orientation, 
            x=x, 
            y=y, 
            first_piece=self.first_turn)