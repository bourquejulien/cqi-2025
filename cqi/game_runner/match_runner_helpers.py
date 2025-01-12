import base64
from dataclasses import dataclass
import json
import logging

from docker.models.containers import Container
from docker.models.networks import Network

from helpers import get_cpu_count, get_memory_MiB

MAX_LOGS = 200
MAX_LOG_LINE_SIZE = 200
DEFAULT_TIMEOUT = 2
GAME_RUNNER_BASE_NAME = "game-runner-managed"

@dataclass
class GameData:
    port: int
    game_networks: list[Network]
    game_server: Container
    offense: Container
    defense: Container

def safe_execute(func: callable, **args) -> bool:
    try:
        func(**args)
        return True
    except Exception as e:
        logging.warning("Failed to execute %s: %s", func.__name__, e)
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

def get_cpu_per_container() -> float:
    return get_cpu_count() / 4

def get_memory_per_container() -> float:
    return get_memory_MiB() / 4
