import random

from .board import Board
from .player import Player, Move
from .piece import Piece

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
                for orientation in Piece.Orientation.__members__.values():
                    if board.check_piece(piece, Piece.Orientation(orientation), x - i, y - j, False):
                        return Move(x - i, y - j, orientation, piece.id)
    
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
    for piece in player.pieces[::-1]:
        move = _get_move_positions(piece, board, positions)
        if move is not None:
            return move

    return Move(0, 0, Piece.Orientation.UP, 0)

def bot_play(player: Player, board: Board) -> Move:
    # Use a predefined location on the first move for all bots
    if player.is_first_move:
        piece_id = random.randint(0, len(player.pieces) - 1)
        return {
            1: Move(0, 0, Piece.Orientation.UP, piece_id),
            2: Move(15, 0, Piece.Orientation.UP, piece_id),
            3: Move(0, 17, Piece.Orientation.UP, piece_id),
            4: Move(17, 17, Piece.Orientation.UP, piece_id)
        }.get(player.id)

    # Player 3 is greedy, the other bots are random
    run_bot = _greedy_play if player.id == 3 else _random_play
    return run_bot(player, board)
