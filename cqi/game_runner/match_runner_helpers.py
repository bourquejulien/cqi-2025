import base64
from dataclasses import dataclass
import json
import logging

from docker.models.containers import Container
from docker.models.networks import Network

from interfaces import Match, GameServerStatus

MAX_LOGS = 100
MAX_LOG_LINE_SIZE = 100

@dataclass
class GameData:
    port: int
    game_network: Network
    game_server: Container
    offense: Container
    defense: Container

@dataclass
class MatchData:
    game: Match
    start_time: float
    game_1: GameData
    game_2: GameData

def safe_execute(func: callable, **args) -> bool:
    try:
        func(**args)
        return True
    except Exception as _:
        return False

def stop_and_remove(container: Container) -> None:
    safe_execute(container.stop, timeout=3)
    safe_execute(container.remove, force=True)

def stop_and_remove_all(*containers: list[Container]) -> None:
    for container in containers:
        stop_and_remove(container)

def get_logs_and_remove(container: Container) -> list[str]:
    logs = []

    safe_execute(container.stop, timeout=3)
    
    try:
        logs = container.logs().decode().split("\n")[-MAX_LOGS:]
        logs = [log[:MAX_LOG_LINE_SIZE] for log in logs]
    except:
        logging.warning("Failed to get logs for container %s", container.name)
        pass

    safe_execute(container.remove, force=True)

    return logs

def get_logs_and_remove_all(*containers: list[Container]) -> list[list[str]]:
    logs = []

    for container in containers:
        logs.append(get_logs_and_remove(container))
    
    return logs

def to_base_64(data) -> str:
    data = json.dumps(data)
    return base64.b64encode(data.encode()).decode()

def build_simple_error(message: str) -> dict:
    return {
        "errorType": "simple",
        "message": message
    }

def build_detailed_error(data: MatchData, statuses: list[GameServerStatus], logs: list[list[str]]) -> dict:
    assert len(statuses) == 2
    message = "\n\n".join([status.gameData["errorMessage"] for i, status in enumerate(statuses) if status.gameData["errorMessage"] is not None])
   
    return {
        "errorType": "detailed",
        "message": message,
        "matches": [{
                "offenseTeamId": data.game.team1_id,
                "defenseTeamId": data.game.team2_id,
                "logs": {
                    "offense": logs[0],
                    "defense": logs[1]
                }
            },
            {
                "offenseTeamId": data.game.team2_id,
                "defenseTeamId": data.game.team1_id,
                "logs": {
                    "offense": logs[2],
                    "defense": logs[3]
            }
        }]
    }

def build_game_data(data: MatchData, statuses: list[GameServerStatus], logs: list[list[str]]) -> dict:
    assert len(statuses) == 2

    return {
        "matches": [
            {
                "offenseTeamId": data.game.team1_id,
                "defenseTeamId": data.game.team2_id,
                "logs": {
                    "offense": logs[0],
                    "defense": logs[1]
                },
                "steps": statuses[0].gameData["steps"]
            },
            {
                "offenseTeamId": data.game.team2_id,
                "defenseTeamId": data.game.team1_id,
                "logs": {
                    "offense": logs[2],
                    "defense": logs[3]
                },
                "steps": statuses[1].gameData["steps"]
            }
        ]
    }
