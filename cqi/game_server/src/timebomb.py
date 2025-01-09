from game_server_common.base import ElementType, Position

from .logger import Level, Logger
from .map import Map

TIMEBOMB_DURATION = 10
TIMEBOMB_COOLDOWN = 3
COUNTDOWN_START = 3


class Timebomb:
    _map: Map
    _logger: Logger

    _steps_since_last_timebomb: int
    _position: Position | None
    _countdown: int | None

    def __init__(self, map: Map, logger: Logger) -> None:
        self._map = map
        self._logger = logger

        self._steps_since_last_timebomb = 0
        self._position = None
        self._countdown = None

    @property
    def skip_offense(self) -> bool:
        return self._countdown is not None and self._countdown <= 0
    
    @property
    def can_add(self) -> bool:
        return self._countdown is None and self._steps_since_last_timebomb >= TIMEBOMB_COOLDOWN

    def play(self) -> None:
        if self._countdown is None:
            self._steps_since_last_timebomb += 1
            return
        
        self._steps_since_last_timebomb = 0
        self._countdown -= 1

        if self._countdown > 0:
            self._tik()
            return

        if self._countdown == 0:
            self._explode()
            return

        self._wait()
        
    def drop(self, bomb_position: Position, player_position: Position) -> bool:
        if not self.can_add:
            self._logger.add(f"Cannot add timebomb, either a bomb is already present or the cooldown period is not over", Level.INFO)
            return False
        
        self._map.set(bomb_position.x, bomb_position.y, ElementType.TIMEBOMB)

        if not self._map.path_exists(player_position):
            self._logger.add(f"Cannot add timebomb, no path from player to goal", Level.INFO)
            self._map.set(bomb_position.x, bomb_position.y, ElementType.BACKGROUND)
            return False
        
        self._position = bomb_position
        self._countdown = COUNTDOWN_START
        self._steps_since_last_timebomb = 0
        self._map.set(bomb_position.x, bomb_position.y, ElementType.TIMEBOMB)
        self._logger.add(f"Timebomb added at {bomb_position}, will explode in {COUNTDOWN_START} steps", Level.INFO)

    def _reset(self) -> None:
        self._steps_since_last_timebomb = 0
        self._map.set(self._position.x, self._position.y, ElementType.BACKGROUND)

        self._position = None
        self._countdown = None
    
    def _explode(self) -> None:
        if any(tile.element == ElementType.PLAYER_OFFENSE for tile, _ in self._map.get_nearby_tiles(*self._position)):
            self._logger.add("Timebomb exploded, player was caught in the explosion", Level.INFO)
            return

        self._logger.add("Timebomb exploded, the player escaped the explosion", Level.INFO)
        self._reset()

    def _wait(self) -> None:
        if self._countdown > -TIMEBOMB_DURATION:
            return
        
        self._logger.add(f"Timebomb explosion has ended", Level.INFO)
        self._reset()

    def _tik(self) -> None:
        match self._countdown:
            case 2:
                self._map.set(self._position.x, self._position.y, ElementType.TIMEBOMB_SECOND_ROUND)
            case 1:
                self._map.set(self._position.x, self._position.y, ElementType.TIMEBOMB_THIRD_ROUND)
        
        self._logger.add(f"Timebomb at {self._position} will explode in {self._countdown} steps", Level.INFO)
