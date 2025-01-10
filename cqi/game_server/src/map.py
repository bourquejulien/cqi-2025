#!/bin/env python3

from game_server_common.base import *
from game_server_common.map import Map as CommonMap, Tile

from PIL import Image
from io import BytesIO
import logging

import random
import numpy as np
import base64

TILE_SIZE = 20

class Map(CommonMap):
    width: int
    height: int

    goal: Position

    def __init__(self, map: np.ndarray) -> None:
        super().__init__(map)
        self.width = map.shape[0]
        self.height = map.shape[1]

        self._set_goal()

    def _set_goal(self) -> None:
        self.goal = Position(self.width - 1, random.randint(0, self.height - 1)) 
        self.map[self.goal.x, self.goal.y] = ElementType.GOAL.value

    def __str__(self) -> str:
        return str(self.map)
    
    def __repr__(self) -> str:
        return repr(self.map)
    
    def get_surrounding_tiles(self, x, y) -> list[Tile]:
        if self.get(x, y) is None:
            return []

        tiles = [tile for tile, _ in self.get_nearby_tiles(x, y)]
        tiles.append(self.get(x - 1, y + 1))
        tiles.append(self.get(x + 1, y - 1))
        tiles.append(self.get(x + 1, y + 1)) 
        tiles.append(self.get(x - 1, y - 1))

        return [tile for tile in tiles if tile is not None]
    
    def to_list(self) -> list[list[str]]:
        return [[str(row) for row in col] for col in self.map.tolist()]
    
    def to_img_64(self, offense_position: Position, visibility_range: int = None) -> bytes:
        """Creates a base64 image of the map"""
        image = Image.new("RGB", (self.width * TILE_SIZE, self.height * TILE_SIZE), color = ElementType.BACKGROUND.to_color())

        def img_paste(x :int, y: int, type: ElementType):
            image.paste(type.to_color(), (x * TILE_SIZE, y * TILE_SIZE, (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
        
        for x in range(self.width):
            for y in range(self.height):
                element_type = ElementType(self.map[x, y])
                if element_type is not ElementType.BACKGROUND:
                    img_paste(x, y, element_type)

        if visibility_range is not None:
            left = max(0, offense_position.x - visibility_range)
            right = min(self.width, offense_position.x + visibility_range)
            upper = max(0, offense_position.y - visibility_range)
            lower = min(self.height, offense_position.y + visibility_range)
            image = image.crop(tuple([value * TILE_SIZE for value in [left, upper, right + 1, lower + 1]]))

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    def set_full_vision(self):
        large_vision: Position = Position(random.randint(0, self.width - 1), random.randint(0, self.height - 1))

        if self.get(large_vision.x, large_vision.y).element != ElementType.BACKGROUND:
            self.set_full_vision()
            return

        self.map[large_vision.x, large_vision.y] = ElementType.LARGE_VISION.value

    def get_shortest_path(self, start: Position) -> list[Position]:
        path_map = self.map.copy()
        end = self.goal

        queue: list[list[Position]] = []
        queue.append([start])
        path_map[start.x, start.y] = ElementType.VISITED.value

        while(len(queue) > 0):
            path: list[Position] = queue.pop(0)
            point = path[-1]

            if point.x == end.x and point.y == end.y:
                break

            # Check other points
            next_points = [Position(point.x + 1, point.y), Position(point.x - 1, point.y), Position(point.x, point.y + 1), Position(point.x, point.y - 1)]
            for next_point in next_points:
                if next_point.x >= 0 and next_point.x < path_map.shape[0] and next_point.y >= 0 and next_point.y < path_map.shape[1]:
                    if path_map[next_point.x, next_point.y] in [ElementType.BACKGROUND.value, ElementType.GOAL.value, ElementType.LARGE_VISION.value]:
                        path_map[next_point.x, next_point.y] = ElementType.VISITED.value
                        queue.append(path + [next_point])
            
        return path

    def path_exists(self, start: Position) -> bool:
        path_map = self.map.copy()
        end = self.goal

        queue = []
        queue.append(start)
        path_map[start.x, start.y] = ElementType.VISITED.value

        valid_path = False
        while(len(queue) > 0):
            point: Position = queue.pop(0)

            if point.x == end.x and point.y == end.y:
                valid_path = True
                break

            # Check other points
            next_points = [Position(point.x + 1, point.y), Position(point.x - 1, point.y), Position(point.x, point.y + 1), Position(point.x, point.y - 1)]
            for next_point in next_points:
                if next_point.x >= 0 and next_point.x < self.width and next_point.y >= 0 and next_point.y < self.height:
                    if path_map[next_point.x, next_point.y] in [ElementType.BACKGROUND.value, ElementType.GOAL.value, ElementType.LARGE_VISION.value]:
                        path_map[next_point.x, next_point.y] = ElementType.VISITED.value
                        queue.append(next_point)

        return valid_path

    @classmethod
    def create_map(cls, width: int = 20, height: int = 20):
        return cls(np.array([[ElementType.BACKGROUND.value] * width] * height))
