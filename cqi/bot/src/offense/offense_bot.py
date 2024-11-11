import random
import logging
import game_server_common.helpers as helpers

from dataclasses import dataclass
import numpy as np
from game_server_common.map import Map, Tile
from game_server_common.base import ElementType, Position, OffenseMove, OffenseMove


@dataclass
class Entry:
    available_moves: set[OffenseMove]
    played_moves: set[OffenseMove]


@dataclass
class Limits:
    left: int | None
    right: int | None
    top: int | None
    bottom: int | None


class DumbOffenseBot:
    map: dict[Position, Entry]
    block_size: tuple[int, int]
    current_position: Position
    limits: Limits

    # feilds for aggregate map
    prev_move: OffenseMove | None
    aggregate_map: Map | None
    map_position: Position | None

    def __init__(self) -> None:
        self.map = dict()
        self.block_size = None
        self.current_position = Position(0, 0)
        self.limits = Limits(None, None, None, None)

        self.prev_move = None
        self.aggregate_map = None
        self.map_position = None

    # Assumes that the player makes a valid move each turn
    def _aggregate_map(self, new_map: Map, player_rel_pos: Position) -> None:
        if self.prev_move is None or self.aggregate_map is None:
            self.aggregate_map = new_map
            self.map_position = player_rel_pos
            return
        
        # Calculate the offset of the new map relative to the old map using the previous move direction
        offset: Position = Position(0, 0)
        if self.prev_move == OffenseMove.UP:
            offset = Position(0, -1)
        elif self.prev_move == OffenseMove.DOWN:
            offset = Position(0, 1)
        elif self.prev_move == OffenseMove.LEFT:
            offset = Position(-1, 0)
        elif self.prev_move == OffenseMove.RIGHT:
            offset = Position(1, 0)

        map_offset = (self.map_position + offset) - player_rel_pos  # Offset to go from new_map to old_map

        origin_new = Position(0, 0) + map_offset
        end_new = Position(new_map.map.shape[0], new_map.map.shape[1]) + map_offset

        aggregate_width = max(end_new.x, self.aggregate_map.map.shape[0]) - min(origin_new.x, 0)
        aggregate_height = max(end_new.y, self.aggregate_map.map.shape[1]) - min(origin_new.y, 0)
        aggregate_map = np.full((aggregate_width, aggregate_height), ElementType.UNKNOW.value)

        # Compute 0,0 of old map in aggregate map
        old_x_offset = 0 if origin_new.x >= 0 else abs(origin_new.x)
        old_y_offset = 0 if origin_new.y >= 0 else abs(origin_new.y)
        aggregate_map[old_x_offset:old_x_offset + self.aggregate_map.map.shape[0], old_y_offset:old_y_offset + self.aggregate_map.map.shape[1]] = self.aggregate_map.map

        # Compute 0,0 of new map in aggregate map
        new_x_offset = map_offset.x + old_x_offset
        new_y_offset = map_offset.y + old_y_offset
        aggregate_map[new_x_offset:new_x_offset + new_map.map.shape[0], new_y_offset:new_y_offset + new_map.map.shape[1]] = new_map.map

        self.aggregate_map = Map(aggregate_map)
        player_x, player_y = np.where(
            self.aggregate_map.map == ElementType.PLAYER_OFFENSE.value)
        self.map_position = Position(int(player_x[0]), int(player_y[0]))

    def _move_priority(self) -> list[OffenseMove]:
        if self.limits.right is None or (self.limits.right - self.current_position.x) > 2:
            moves = [OffenseMove.UP, OffenseMove.DOWN]
            random.shuffle(moves)
            moves.insert(0, OffenseMove.RIGHT)
            moves.append(OffenseMove.LEFT)
            return moves

        if self.limits.top is None:
            return [OffenseMove.UP, OffenseMove.RIGHT, OffenseMove.LEFT, OffenseMove.DOWN]

        if self.limits.bottom is None:
            return [OffenseMove.DOWN, OffenseMove.RIGHT, OffenseMove.LEFT, OffenseMove.UP]

        is_closer_to_top = abs(
            self.limits.top - self.current_position.y) < (self.limits.bottom - self.current_position.y)
        if is_closer_to_top:
            return [OffenseMove.DOWN, OffenseMove.RIGHT, OffenseMove.LEFT, OffenseMove.UP]
        return [OffenseMove.UP, OffenseMove.RIGHT, OffenseMove.LEFT, OffenseMove.DOWN]

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
            available_moves = self._process_entry(entry, available_moves)
        else:
            entry = Entry({move for _, move in moves}, set())
            self.map[self.current_position] = entry

        logging.info(available_moves)

        chosen_move: tuple[Tile, OffenseMove] | None = None
        if goal_pos is not None:
            chosen_move = min([(tile.position.to(goal_pos), move)
                              for tile, move in available_moves], key=lambda x: x[0])[1]
        else:
            moves = self._move_priority()

            for move in moves:
                if move in [move for _, move in available_moves]:
                    chosen_move = move
                    break

        entry.played_moves.add(chosen_move)
        return chosen_move

    def _set_map_limits(self, nearby_tiles: list[tuple[Tile, OffenseMove]]):
        available_moves = {move for _, move in nearby_tiles}

        if OffenseMove.LEFT not in available_moves:
            self.limits.left = self.current_position.x
        if OffenseMove.RIGHT not in available_moves:
            self.limits.right = self.current_position.x
        if OffenseMove.UP not in available_moves:
            self.limits.top = self.current_position.y
        if OffenseMove.DOWN not in available_moves:
            self.limits.bottom = self.current_position.y

    def play(self, img: str) -> OffenseMove | None:
        if not (data := self._parse_map(img)):
            return None
        map, map_pos, goal_pos = data

        self._aggregate_map(map, map_pos)
        logging.info(f"Full map: {self.aggregate_map.to_img_64().decode()}")

        nearby_tiles = map.get_nearby_tiles(*map_pos)
        self._set_map_limits(nearby_tiles)
        available_moves = [tile for tile in nearby_tiles if tile[0].element in [
            ElementType.BACKGROUND, ElementType.GOAL]]
        logging.info(available_moves)

        if len(available_moves) == 0:
            return None

        move = self._play_best_move(available_moves, map_pos, goal_pos)
        if move != None:
            self._set_current_position(move)

        self.prev_move = move
        return move
