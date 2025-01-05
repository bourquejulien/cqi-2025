from .bots import DefenseBot
from game_server_common import helpers
from game_server_common.base import DefenseMove, ElementType, Position
from game_server_common.map import Map


class Defense:
    block_size: tuple[int, int] | None
    bot: DefenseBot

    def __init__(self, bot: DefenseBot) -> None:
        self.block_size = None
        self.bot = bot

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

    def play(self, img: str) -> tuple[DefenseMove, Position] | None:
        if not (map := self._parse_map(img)):
            return None

        return self.bot.play(map)
