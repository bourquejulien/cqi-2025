import numpy as np
import game_server_common.helpers as helpers

from game_server_common.map import Map
from game_server_common.base import ElementType, Position, DefenseMove


class RandomDefenseBot:
    block_size: tuple[int, int]

    def __init__(self) -> None:
        self.last_event = None
        self.block_size = None

    def _parse_map(self, img: str) -> Map | None:
        data = helpers.parse_base64(img)

        if self.block_size is None:
            block_size = helpers.get_block_size(
                data, ElementType.PLAYER_OFFENSE.to_color())
            if block_size is None:
                return None
            self.block_size = block_size

        data = helpers.parse_data(data, self.block_size)

        return data[0]

    def play(self, img: str) -> tuple[DefenseMove, Position]:
        if not (map := self._parse_map(img)):
            return None

        # Chose a random tile that has nothing on it
        xidx, yidx = np.where(map.map == ElementType.BACKGROUND.value)
        idx = np.random.choice(np.arange(len(xidx)))
        position: Position = Position(int(xidx[idx]), int(yidx[idx]))

        return DefenseMove.WALL, position
