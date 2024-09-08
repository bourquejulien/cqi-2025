from board import Board
from player import Player
from piece import Piece
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

def get_move_positions(piece: Piece, board: Board, positions: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    for x, y in positions:
        for i in range(piece.size):
            for j in range(piece.size):
                for orientation in range(4):
                    if board.check_piece(piece, Piece.Orientation(orientation), x - i, y - j, False):
                        return (x - i, y - j, orientation, piece.id)
    
    return None

def random_play(player: Player, board: Board) -> tuple[int, int, int, int]:
    positions = edge_tiles(player, board)

    # Choose a piece at random 20 times
    for i in range(20):
        piece = random.choice(player.pieces)
        move = get_move_positions(piece, board, positions)
        if move:
            return move

    return (0, 0, 0, 0)

def greedy_play(player: Player, board: Board) -> tuple[int, int, int, int]:
    positions = edge_tiles(player, board)

    # Iterate over piece in reverse order (i.e. from largest to smallest)
    for piece in player.pieces[::-1]:
        move = get_move_positions(piece, board, positions)
        if move:
            return move

    return (0, 0, 0, 0)

