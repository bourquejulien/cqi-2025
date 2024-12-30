from dataclasses import dataclass
import numpy as np


@dataclass
class GameStatus:
    map: np.ndarray

@dataclass
class RunnerStatus:
    is_running: bool
    is_over: bool
    score: int | None
    game_status: dict | None

@dataclass
class GameResult:
    id: str
    winner_id: str | None
    is_error: bool
    team1_score: float
    team2_score: float
    error_data: str | None
    game_data: str | None

@dataclass
class Match:
    id: str
    team1_id: str
    team2_id: str
    image_team1: str
    image_team2: str
