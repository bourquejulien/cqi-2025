from dataclasses import dataclass
from threading import RLock
import time

from src.game_handler import GameHandler, GameData


@dataclass
class GameServerStatus:
    is_running: bool
    is_over: bool
    score: float
    game_data: GameData | None

    def __iter__(self):
        yield "isRunning", self.is_running
        yield "isOver", self.is_over
        yield "score", self.score
        yield "gameData", dict(self.game_data) if self.game_data is not None else None

class Runner:
    game_lock: RLock
    data_lock: RLock
    should_stop: bool
    game_status: GameServerStatus

    game_handler: GameHandler | None

    def __init__(self) -> None:
        self.game_lock = RLock()
        self.data_lock = RLock()
        self.should_stop = False
        self.game_handler = None

        self._update_status()

    @property
    def is_active(self) -> bool:
        return self.game_handler is not None
    
    @property
    def is_over(self) -> bool:
        return self.game_handler is not None and self.game_handler.is_over

    @property
    def is_running(self) -> bool:
        with self.game_lock:
            return self.is_active and not self.is_over

    def run(self):
        while not self.should_stop:
            if not self.is_running:
                time.sleep(1)
            with self.game_lock:
                self._handle_game()
        self.force_end_game()

    def stop(self):
        self.should_stop = True

    def launch_game(self, offense_bot_url: str, defense_bot_url: str, seed: str) -> None:
        if self.is_active:
            return

        with self.game_lock:
            if self.is_active:
                return
            self.game_handler = GameHandler(offense_bot_url, defense_bot_url, seed)
        self._update_status()

    def force_end_game(self) -> bool:
        if not self.is_active:
            return False

        with self.game_lock:
            if not self.is_active:
                return False

            self.game_handler.end_game()
            self.game_handler = None
            self._update_status()

    def status(self) -> GameServerStatus:
        return self.game_status

    def _handle_game(self) -> None:
        if not self.is_running:
            self._update_status()
            return

        if not self.game_handler.is_started:
            self.game_handler.start_game()
        
        self.game_handler.play()
        self._update_status()

    def _update_status(self) -> None:
        game_status = GameServerStatus(self.is_running,
                                        self.is_over,
                                        self.game_handler.score if self.is_active else 0,
                                        self.game_handler.get_data() if self.is_over else None)
        self.game_status = game_status
