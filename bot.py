from board import Board
from player import Player
import random

def edge_tiles(player: Player, board: Board) -> list[tuple[int, int]]:
    edge_tiles = set()
    for i in range(board.width):
        for j in range(board.height):
            if board.board[i][j] == player.id:
                # Check empty diagonal tiles
                if i + 1 < board.width and j + 1 < board.height:
                    if board.board[i + 1][j + 1] == 0:
                        edge_tiles.add((i + 1, j + 1))
                if i - 1 >= 0 and j + 1 < board.height:
                    if board.board[i - 1][j + 1] == 0:
                        edge_tiles.add((i - 1, j + 1))
                if i + 1 < board.width and j - 1 >= 0:
                    if board.board[i + 1][j - 1] == 0:
                        edge_tiles.add((i + 1, j - 1))
                if i - 1 >= 0 and j - 1 >= 0:
                    if board.board[i - 1][j - 1] == 0:
                        edge_tiles.add((i - 1, j - 1))
    
    return list(edge_tiles)

def random_play(player: Player, board: Board):
    # Choose a peice at random
    peice_id = random.randint(0, player.pieces_remaining)
    
    

def greedy():
    pass

