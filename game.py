from board import Board
from peice import Peice
from player import Player
import random

# Create the board class
board: Board = Board.simple_board()

# Create the players
player_1 = Player(1)
player_2 = Player(2)
player_3 = Player(3)
player_4 = Player(4)

players = [player_1, player_2, player_3, player_4]

# Radomize the starting player
starting_player = random.randint(0, 3)
players = players[starting_player:] + players[:starting_player]

for peice in players[0].peices:
    peice.to_img(Peice.Orientation.UP, name=f"peice/peice_{peice.id}")

# The game loop
playing = True
first_peice = True

# Start the game for each player
for player in players:
    player.playing = True

while playing:
    for i, player in enumerate(players):
        
        # If the player is not playing skip him
        if not player.playing:
            continue

        # Print the board
        img: bytes = board.to_img()

        # TODO - SEND THE BOARD TO THE NEXT PLAYER

        # TODO - IMPLEMENT AGENT TO CHOOSE A MOVE HERE

        # Play the move
        # If the move is invalid the player will not play anymore
        player.playing = player.play(board, 4, Peice.Orientation.LEFT, 0, 0, first_peice=first_peice)

        # If the has no more peices the game is over
        if player.peices_remaining == 0:
            playing = False
            break
    
    # The first peice has been played for each player
    first_peice = False

    # if no player is playing the game is over
    if not any([player.playing for player in players]):
        playing = False
    
    
