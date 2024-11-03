from enum import Enum
import PIL.ImageColor
import numpy as np
import base64
import io
import PIL
from PIL import Image
from .base import *

from .map import Map


def parse_base64(data: str) -> np.ndarray:
    decoded = base64.b64decode(data)
    image = Image.open(io.BytesIO(decoded))
    return np.array(image)

def rgb_to_element(r: int, g: int, b: int) -> ElementType | None:
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b).upper()

    for element, color in ELEMENT_TYPE_TO_COLOR.items():
        if color == hex_color:
            return element
    
    return None


def get_block_size(data: np.array, color: str) -> tuple[int, int] | None:
    rgb_color = np.array(PIL.ImageColor.getrgb(color))

    start: tuple[int, int] | None = None
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if (data[i, j] == rgb_color).all():
                start = (i, j)
                break
        if start is not None:
            break

    if start is None:
        return None

    size: list[int, int] = [data.shape[0] - start[0], data.shape[1] - start[1]]
    for i in range(data.shape[0] - start[0]):
        if (data[start[0] + i, start[1]] != rgb_color).any():
            size[0] = i
            break
    for j in range(data.shape[1] - start[1]):
        if (data[start[0], start[1] + j] != rgb_color).any():
            size[1] = j
            break

    return tuple(size)


def parse_data(data: np.ndarray, block_size: tuple[int, int]) -> tuple[Map, dict[ElementType, list[Position]]]:
    size = (data.shape[0] // block_size[0], data.shape[1] // block_size[1])

    element_positions = {ElementType.GOAL: [], ElementType.PLAYER_OFFENSE: []}
    output_map = np.zeros(size)
    
    for i in range(size[0]):
        for j in range(size[1]):
            id = rgb_to_element(*data[i * block_size[0], j * block_size[1]])
            output_map[i, j] = id.value
            
            element = ElementType(id)
            if element in element_positions:
                element_positions[element].append(Position(i, j))

    return Map(output_map), element_positions
