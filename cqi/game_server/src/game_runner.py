import time

from threading import RLock
from logging import Logger

from src.game_handler import GameHandler


class Runner:
    lock: RLock
    should_stop: bool
    logger: Logger

    game_handler: GameHandler | None

    def __init__(self, logger: Logger) -> None:
        self.lock = RLock()
        self.should_stop = False
        self.logger = logger
        self.game_handler = None

    @property
    def is_running(self) -> bool:
        return self.game_handler is not None

    def run(self):
        while not self.should_stop:
            with self.lock:
                self._handle_game()
            time.sleep(1)

        self.force_end_game()

    def stop(self):
        self.should_stop = True

    def launch_game(self, offense_bot_url: str, defense_bot_url: str):
        with self.lock:
            self.game_handler = GameHandler(offense_bot_url, defense_bot_url, self.logger)

    def force_end_game(self) -> bool:
        with self.lock:
            if self.game_handler is None:
                return False

            self.game_handler.force_end_game()
            self.game_handler = None
        
        return True

    def status(self) -> dict:
        with self.lock:
            return {
                "isRunning": self.is_running,
                "gameStatus": self.game_handler.get_status() if self.is_running else None,
            }

    def _handle_game(self) -> None:
        if self.game_handler is None:
            return

        self.game_handler.play()
