import random
import game_server_common.helpers as helpers

from dataclasses import dataclass
from typing import Self
from game_server_common.map import Map, Tile
from game_server_common.base import ElementType, Position, OffenseMove


@dataclass
class Event:
    position: Position
    played_moves: list[OffenseMove]
    last: Self | None


class DumbOffenseBot:
    last_event: Event | None

    def __init__(self) -> None:
        self.last_event = None

    def _parse_map(self, img: str) -> tuple[Map, Position, Position] | None:
        data = helpers.parse_base64(img)

        if not (block_size := helpers.get_block_size(data, ElementType.PLAYER_OFFENSE.to_color())):
            return None

        data = helpers.parse_data(data, block_size)

        map = data[0]
        current_pos = data[1][ElementType.PLAYER_OFFENSE]
        goal_pos = data[1][ElementType.GOAL]

        if len(current_pos) == 0:
            return None

        return map, current_pos[0], goal_pos[0] if len(goal_pos) > 0 else None

    def _play_on_backtrack(self, moves: list[tuple[Tile, OffenseMove]], current_pos: Position) -> OffenseMove | None:
        if not any([self.last_event.last is not None and self.last_event.last == tile.position for tile, _ in moves]):
            self.last_event = Event(current_pos, [], None)
            return None

        filtered_moves = [
            (tile, move) for tile, move in moves if move not in self.last_event.played_moves and tile.position != self.last_event.last.position]
        if len(filtered_moves) == 0:
            self.last_event = self.last_event.last
            return [move for tile, move in moves if tile.position == self.last_event.last.position][0]

        moves.clear()
        moves.extend(filtered_moves)

    def _play_best_move(self, moves: list[tuple[Tile, OffenseMove]], current_pos: Position, goal_pos: Position | None) -> OffenseMove:
        is_backtrack = (not self.last_event ==
                        None) and self.last_event.position == current_pos

        playable_moves: list[tuple[Tile, OffenseMove]] = moves.copy()
        if is_backtrack:
            if move := self._play_on_backtrack(playable_moves, current_pos):
                return move
        else:
            self.last_event = Event(current_pos, [], self.last_event)

        chosen_move: tuple[Tile, OffenseMove] | None = None
        if goal_pos is not None:
            chosen_move = min([(tile.position.to(goal_pos), move)
                              for tile, move in playable_moves], key=lambda x: x[0])[1]
        else:
            all_moves = [OffenseMove.RIGHT, OffenseMove.UP]
            random.shuffle(all_moves)
            all_moves.extend([OffenseMove.DOWN, OffenseMove.LEFT])

            for move in all_moves:
                if move in [move for _, move in playable_moves]:
                    chosen_move = move
                    break

        self.last_event.played_moves.append(chosen_move)
        return chosen_move

    def play(self, img: str) -> OffenseMove | None:
        if not (data := self._parse_map(img)):
            return None
        map, current_pos, goal_pos = data

        available_moves = map.get_nearby_tiles(*current_pos)

        if len(available_moves) == 0:
            return None

        return self._play_best_move(available_moves, current_pos, goal_pos)
