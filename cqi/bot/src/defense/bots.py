from abc import ABC, abstractmethod
import numpy as np
import game_server_common.helpers as helpers

from game_server_common.map import Map
from game_server_common.base import ElementType, Position, DefenseMove


class DefenseBot(ABC):
    @abstractmethod
    def play(self, img: str) -> tuple[DefenseMove, Position] | None:
        pass


class BlockerDefenseBot(DefenseBot):
    n_turn: int

    def __init__(self) -> None:
        self.last_event = None
        self.n_turn = 0

    def play(self, map: Map) -> tuple[DefenseMove, Position] | None:
        # Play once every 2 turns
        self.n_turn += 1
        if self.n_turn % 2 == 0:
            return None

        # Place a block directly in front of the player
        player_x, player_y = np.where(
            map.map == ElementType.PLAYER_OFFENSE.value)
        player_pos: Position = Position(int(player_x[0]), int(player_y[0]))

        goal_x, goal_y = np.where(map.map == ElementType.GOAL.value)
        goal_pos: Position = Position(int(goal_x[0]), int(goal_y[0]))

        if goal_pos.x > player_pos.x:
            wall_pos: Position = Position(player_pos.x + 1, player_pos.y)
        elif goal_pos.y > player_pos.y:
            wall_pos: Position = Position(player_pos.x, player_pos.y + 1)
        else:
            wall_pos: Position = Position(player_pos.x, player_pos.y - 1)

        return DefenseMove.WALL, wall_pos


class RandomDefenseBot(DefenseBot):

    def __init__(self) -> None:
        self.last_event = None

    def play(self, map: Map) -> tuple[DefenseMove, Position]:
        # Chose a random tile that has nothing on it
        xidx, yidx = np.where(map.map == ElementType.BACKGROUND.value)
        idx = np.random.choice(np.arange(len(xidx)))
        position: Position = Position(int(xidx[idx]), int(yidx[idx]))

        return DefenseMove.WALL, position
