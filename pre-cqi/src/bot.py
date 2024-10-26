from collections import deque
import random

from .board import Board, Tile
from .player import Player, Move
from .piece import Piece

# Make the most isolated move in the predefined moves
def _get_first_move(player: Player, board: Board) -> Move:
    piece_id = random.randint(10, len(player.pieces) - 1)
    possible_moves = [Move(0, 0, Piece.Orientation.UP, piece_id), Move(17, 0, Piece.Orientation.UP, piece_id), Move(0, 17, Piece.Orientation.UP, piece_id), Move(17, 17, Piece.Orientation.UP, piece_id)]

    if (board.is_empty):
        return random.choice(possible_moves)

    nearest_tiles: list[tuple[Move, Tile]] = [(move, board.get_nearest_tile(move.x, move.y)) for move in possible_moves]
    best_move, _ = max([(move, abs(move.x - tile.x) + abs(move.y - tile.y)) for move, tile in nearest_tiles], key=lambda x: x[1])

    return best_move

def _edge_tiles(player: Player, board: Board) -> list[tuple[int, int]]:
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

def _get_move_positions(piece: Piece, board: Board, positions: list[tuple[int, int]]) -> Move:
    for x, y in positions:
        for i in range(piece.size):
            for j in range(piece.size):
                posx = x - i
                posy = y - j

                if posx < 0 or posy < 0 or piece.shape[i, j] == None:
                    continue

                for orientation in Piece.Orientation.__members__.values():
                    if board.check_piece(piece, Piece.Orientation(orientation), posx, posy, False):
                        return Move(posx, posy, orientation, piece.id)
    return None

def _random_play(player: Player, board: Board) -> Move:
    positions = _edge_tiles(player, board)

    # Choose a piece at random 20 times
    for _ in range(20):
        piece = random.choice(player.pieces)
        move = _get_move_positions(piece, board, positions)
        if move is not None:
            return move

    return Move(0, 0, Piece.Orientation.UP, 0)

def _greedy_play(player: Player, board: Board) -> Move:
    positions = _edge_tiles(player, board)

    # Iterate over piece in reverse order (i.e. from largest to smallest)
    pieces = player.pieces.copy()
    pieces.sort(key=lambda piece: -piece.size)
    for piece in pieces:
        move = _get_move_positions(piece, board, positions)
        if move is not None:
            return move

    return Move(0, 0, Piece.Orientation.UP, 0)

def bot_play(player: Player, board: Board) -> Move:
    if player.is_first_move:
        # On first move, use predefined locations
        return _get_first_move(player, board)

    run_bot = _greedy_play if random.randint(1, 100) > 50 else _random_play
    return run_bot(player, board)
