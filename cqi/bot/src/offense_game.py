import random
import logging
import game_server_common.helpers as helpers

from dataclasses import dataclass
from typing import Self
from game_server_common.map import Map, Tile
from game_server_common.base import ElementType, Position, OffenseMove, OffenseMove


@dataclass
class Entry:
    available_moves: set[OffenseMove]
    played_moves: set[OffenseMove]


class DumbOffenseBot:
    map: dict[Position, Entry]
    block_size: tuple[int, int]
    current_position: Position

    def __init__(self) -> None:
        self.map = dict()
        self.block_size = None
        self.current_position = Position(0, 0)

    def _parse_map(self, img: str) -> tuple[Map, Position, Position] | None:
        data = helpers.parse_base64(img)

        if self.block_size is None:
            block_size = helpers.get_block_size(
                data, ElementType.PLAYER_OFFENSE.to_color())
            if block_size is None:
                return None
            self.block_size = block_size

        data = helpers.parse_data(data, self.block_size)

        map = data[0]
        current_pos = data[1][ElementType.PLAYER_OFFENSE]
        goal_pos = data[1][ElementType.GOAL]

        if len(current_pos) == 0:
            return None

        return map, current_pos[0], goal_pos[0] if len(goal_pos) > 0 else None

    def _set_current_position(self, move: OffenseMove) -> None:
        self.current_position = self.current_position + move.to_position()

    def _process_entry(self, entry: Entry, moves: list[tuple[Tile, OffenseMove]]) -> tuple[Tile, OffenseMove]:
        offense_moves = {move for _, move in moves}

        should_discard_history = offense_moves != entry.available_moves
        available_moves = [
            move for move in moves if move[1] not in entry.played_moves]

        if should_discard_history or len(available_moves) == 0:
            entry.available_moves = offense_moves
            entry.played_moves.clear()
            return moves

        return available_moves

    def _play_best_move(self, moves: list[tuple[Tile, OffenseMove]], map_pos: Position, goal_pos: Position | None) -> OffenseMove:
        available_moves = moves.copy()

        if entry := self.map.get(self.current_position):
            available_moves = self._process_entry(entry, moves)
        else:
            entry = Entry({move for _, move in moves}, set())
            self.map[self.current_position] = entry

        chosen_move: tuple[Tile, OffenseMove] | None = None
        if goal_pos is not None:
            chosen_move = min([(tile.position.to(goal_pos), move)
                              for tile, move in available_moves], key=lambda x: x[0])[1]
        else:
            all_moves = [OffenseMove.RIGHT, OffenseMove.UP]
            random.shuffle(all_moves)
            all_moves.extend([OffenseMove.DOWN, OffenseMove.LEFT])

            for move in all_moves:
                if move in [move for _, move in available_moves]:
                    chosen_move = move
                    break
        
        entry.played_moves.add(chosen_move)
        return chosen_move

    def play(self, img: str) -> OffenseMove | None:
        if not (data := self._parse_map(img)):
            return None
        map, map_pos, goal_pos = data

        available_moves = [tile for tile in map.get_nearby_tiles(*map_pos) if tile[0].element in [ElementType.BACKGROUND, ElementType.GOAL]]

        if len(available_moves) == 0:
            return None

        move = self._play_best_move(available_moves, map_pos, goal_pos)
        if move != None:
            self._set_current_position(move)

        return move
