import numpy as np
import game_server_common.helpers as helpers

from game_server_common.map import Map
from game_server_common.base import ElementType, Position, DefenseMove


class RandomDefenseBot:

    def _parse_map(self, img: str) -> Map | None:
        data = helpers.parse_base64(img)

        if not (block_size := helpers.get_block_size(data, ElementType.PLAYER_OFFENSE.to_color())):
            return None

        data = helpers.parse_data(data, block_size)

        return data[0]

    def play(self, img: str) -> tuple[DefenseMove, Position]:
        if not (map := self._parse_map(img)):
            return None

        # Chose a random tile that has nothing on it
        xidx, yidx = np.where(map.map == ElementType.BACKGROUND.value)
        idx = np.random.choice(np.arange(len(xidx)))
        position: Position = Position(xidx[idx], yidx[idx])

        return DefenseMove.WALL, position
