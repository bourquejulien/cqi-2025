from dataclasses import dataclass
from enum import Enum
import logging
from typing import Iterator

class Level(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

@dataclass
class GameStep:
    map: list[list[str]]
    logs: list[str]
    score: int
    visionRadius: int

    def __iter__(self) -> Iterator:
        yield "map", self.map
        yield "logs", self.logs
        yield "score", self.score
        yield "visionRadius", self.visionRadius

class Logger:
    _history: list[GameStep]
    _current_step: GameStep

    def __init__(self):
        self._history = []
        self._current_step = GameStep([], [], 0, 0)
    
    def get(self) -> list[GameStep]:
        return self._history.copy()

    def add(self, message: str, level: Level):
        logging.log(level.value, message)

        if level.value >= Level.INFO.value: 
            self._current_step.logs.append(f"{level.name}: {message}")

    def add_step(self, map: list[list[str]], score: int, visionRadius: int):
        logging.info(f"Round {len(self._history)}, Score: {score}" if len(self._history) > 0 else "Game started")
        self._current_step.map = map
        self._current_step.score = score
        self._current_step.visionRadius = visionRadius
        self._history.append(self._current_step)
        self._current_step = GameStep([], [], 0, 0)
