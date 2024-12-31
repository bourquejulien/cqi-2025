import logging
import game_server_common.helpers as helpers
import numpy as np

from game_server_common.map import Map
from game_server_common.base import ElementType, Position, OffenseMove
from collections import deque

class ShortestPathBot:
    block_size: tuple[int, int]
    prev_move: OffenseMove | None
    aggregate_map: Map | None
    map_position: Position | None
    top_found = False
    bottom_found = False

    def __init__(self) -> None:
        self.block_size = None
        self.prev_move = None
        self.aggregate_map = None
        self.map_position = None
        self.view_range = None

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

        if len(current_pos) == 0:
            return None

        return map, current_pos[0]

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

    def _identify_target(self, view_range) -> Position:
        # Check if the goal is in view
        goal_x, goal_y = np.where(
            self.aggregate_map.map == ElementType.GOAL.value)
        
        if len(goal_x) != 0 and len(goal_y) != 0:
            return Position(int(goal_x[0]), int(goal_y[0]))
        
        # If we discovered the right edge of the map
        if self.map_position.x + view_range >= self.aggregate_map.map.shape[0]:
            target_x = self.map_position.x    
        else:
            target_x = self.aggregate_map.map.shape[0] - 1

        if self.map_position.y - view_range < 0:
            target_y = self.aggregate_map.map.shape[1] - 1
            self.top_found = True
        elif self.map_position.y + view_range >= self.aggregate_map.map.shape[1]:
            target_y = 0
            self.bottom_found = True
        elif self.top_found:
            target_y = self.aggregate_map.map.shape[1] - 1
        elif self.bottom_found:
            target_y = 0
        else:
            target_y = 0
        
        # TODO - Handle cases where target is a wall or obstacle
        return Position(target_x, target_y)        

    def play(self, img: str) -> OffenseMove | None:
        if not (data := self._parse_map(img)):
            return None
        current_map, map_pos = data

        # Range of view of the player
        view_range = max(current_map.map.shape[0] - map_pos.x - 1, map_pos.x)
        
        self._aggregate_map(current_map, map_pos)
        logging.debug(f"Map: {self.aggregate_map.to_img_64().decode()}")

        target: Position = self._identify_target(view_range)
        logging.debug(f"Target: {target}")

        # TODO - Compute shortest path to goal
        path_map = self.aggregate_map.map.copy()
        path_map[target.x, target.y] = ElementType.BACKGROUND.value

        queue: list[list[Position]] = []
        queue.append([self.map_position])
        path_map[self.map_position.x, self.map_position.y] = ElementType.VISITED.value

        while(len(queue) > 0):
            path: list[Position] = queue.pop(0)
            point = path[-1]

            if point.x == target.x and point.y == target.y:
                break

            # Check other points
            next_points = [Position(point.x + 1, point.y), Position(point.x - 1, point.y), Position(point.x, point.y + 1), Position(point.x, point.y - 1)]
            for next_point in next_points:
                if next_point.x >= 0 and next_point.x < path_map.shape[0] and next_point.y >= 0 and next_point.y < path_map.shape[1]:
                    if path_map[next_point.x, next_point.y] in [ElementType.BACKGROUND.value, ElementType.GOAL.value, ElementType.UNKNOW.value]:
                        path_map[next_point.x, next_point.y] = ElementType.VISITED.value
                        queue.append(path + [next_point])
        
        next_spot = path[1]
        if next_spot.x < self.map_position.x:
            move = OffenseMove.LEFT
        elif next_spot.x > self.map_position.x:
            move = OffenseMove.RIGHT
        elif next_spot.y < self.map_position.y:
            move = OffenseMove.UP
        else:
            move = OffenseMove.DOWN

        self.prev_move = move
        return move