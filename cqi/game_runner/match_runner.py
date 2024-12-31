import base64
from dataclasses import dataclass
import json
import logging
import socket
import time
from datetime import datetime, timezone, timedelta

from docker import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network
from docker.models.images import Image

import requests

from stop_token import StopToken
from interfaces import GameResult, Match, GameServerStatus

MAX_LOGS = 100
MAX_LOG_LINE_SIZE = 100
MATCH_EXPIRATION_TIMEOUT_MINUTES = 5
GAME_RUNNER_BASE_NAME = "game-runner-managed"
DEFAULT_TIMEOUT = 2

def get_available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        return port

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
    team_ids = [data.game.team1_id, data.game.team2_id]
    message = "\n".join([f"{team_ids[i]}: {status.gameData["errorMessage"]}" for i, status in enumerate(statuses) if status.gameData["errorMessage"] is not None])
   
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

class MatchRunner:
    game_server_image: Image
    docker_client: DockerClient

    current_matches: dict[str, MatchData]
    results: list[GameResult]

    def __init__(self, game_server_image: Image, docker_client: DockerClient) -> None:
        self.game_server_image = game_server_image
        self.docker_client = docker_client

        self.current_matches = {}
        self.results = []
    
    @property
    def currently_running(self) -> int:
        return len(self.current_matches)
    
    def run_matches(self, stop_token: StopToken, matches: list[Match]) -> None:
        for match in matches:
            self._run_match(stop_token, match)

        for current_match in self.current_matches.values():
            self.get_match_results(stop_token, current_match)
        
        for result in self.results:
            if result.id in self.current_matches:
                del self.current_matches[result.id]
        
        if stop_token.is_canceled():
            self.cleanup()

    def cleanup(self, id: str | None = None) -> None:
        id = id or ""
        start_string = GAME_RUNNER_BASE_NAME + "-" + (id[:8] or "")

        container: Container
        for container in self.docker_client.containers.list(all=True):
            if container.name.startswith((start_string)):
                container.remove(force=True)

        for network in self.docker_client.networks.list():
            if network.name.startswith(start_string):
                for container in network.containers:
                    network.disconnect(container, force=True)
                    container.remove(force=True)
                network.remove()
    
    def get_results(self) -> list[GameResult]:
        results = self.results.copy()
        self.results.clear()

        return results

    def _handle_error(self, match: Match, error: str) -> None:
        logging.error("Failed to run match %s: %s", match.id, error)
        self.cleanup(match.id)

        self.results.append(GameResult(id=match.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=to_base_64(build_simple_error(error)), game_data=None))

    def _run_match(self, stop_token: StopToken, match: Match) -> None:
        if stop_token.is_canceled():
            return

        # Pull images
        try:
            team1_image: Image = self.docker_client.images.pull(match.image_team1)
        except:
            self._handle_error(match, "Failed to pull image: " + match.image_team1)
            return

        try:
            team2_image: Image = self.docker_client.images.pull(match.image_team2)
        except:
            self._handle_error(match, "Failed to pull image" + match.image_team2)
            return

        # Create network
        base_docker_id = f"{GAME_RUNNER_BASE_NAME}-{match.id[:8]}"

        game_network_1: Network
        game_network_2: Network
        try:
            game_network_1 = self.docker_client.networks.create(f"{base_docker_id}-1", driver="bridge") # TODO - Make network internal only
            game_network_2 = self.docker_client.networks.create(f"{base_docker_id}-2", driver="bridge") # TODO - Make network internal only
        except:
            self._handle_error(match, "Failed to create network")
            return
        
        if stop_token.is_canceled():
            return

        # Create containers
        # TODO - Add memory limit and CPU limit
        port_1 = get_available_port()
        port_2 = get_available_port()

        game_server_1: Container
        game_server_2: Container
        try:
            game_server_1 = self.docker_client.containers.create(self.game_server_image, name=f"{base_docker_id}-1", hostname="game_server", ports={"5000":port_1}, network=game_network_1.name)
            game_server_2 = self.docker_client.containers.create(self.game_server_image, name=f"{base_docker_id}-2", hostname="game_server", ports={"5000":port_2}, network=game_network_2.name)

            game_server_1.start()
            game_server_2.start()
        except:
            self._handle_error(match, "Failed to create game server")
            return
        
        if stop_token.is_canceled():
            return
        
        # Start team 1 bots
        team1Offense: Container
        team1Defense: Container
        try:
            team1Offense = self.docker_client.containers.create(team1_image, name=f"{base_docker_id}-{match.team1_id}-O", hostname=f"offense", network=game_network_1.name)
            team1Defense = self.docker_client.containers.create(team1_image, name=f"{base_docker_id}-{match.team1_id}-D", hostname=f"defense", network=game_network_2.name)
            team1Offense.start()
            team1Defense.start()
        except:
            self._handle_error(match, f"Failed to create team {match.team1_id} bots")
            return
        
        if stop_token.is_canceled():
            return
        
        # Start team 2 bots
        team2Offense: Container
        team2Defense: Container
        try:
            team2Offense = self.docker_client.containers.create(team2_image, name=f"{base_docker_id}-{match.team2_id}-O", hostname=f"offense", network=game_network_2.name)
            team2Defense = self.docker_client.containers.create(team2_image, name=f"{base_docker_id}-{match.team2_id}-D", hostname=f"defense", network=game_network_1.name)
            team2Defense.start()
            team2Offense.start()
        except:
            self._handle_error(match, f"Failed to create team {match.team2_id} bots")
            return
        
        if stop_token.is_canceled():
            return

        # Start both games
        game_1_started = False
        game_2_started = False
        for _ in range(5):
            time.sleep(1)

            try:
                if not game_1_started:
                    r1 = requests.post(f"http://localhost:{port_1}/run_game", timeout=DEFAULT_TIMEOUT, params={"offense_url": f"http://offense:5000", "defense_url": f"http://defense:5000", "seed": match.id})
                    game_1_started = r1.ok
                
                if not game_2_started:
                    r2 = requests.post(f"http://localhost:{port_2}/run_game", timeout=DEFAULT_TIMEOUT, params={"offense_url": f"http://offense:5000", "defense_url": f"http://defense:5000", "seed": match.id})
                    game_2_started = r2.ok
            except:
                pass

        if not game_1_started or not game_2_started:
            self._handle_error(match, "Failed to start games")
            return

        game_data_1 = GameData(port=port_1, game_network=game_network_1, game_server=game_server_1, offense=team1Offense, defense=team1Defense)
        game_data_2 = GameData(port=port_2, game_network=game_network_2, game_server=game_server_2, offense=team2Offense, defense=team2Defense)
        match_data = MatchData(game=match, start_time=datetime.now(timezone.utc), game_1=game_data_1, game_2=game_data_2)

        self.current_matches[match_data.game.id] = match_data

    def get_match_results(self, stop_token: StopToken, match_data: MatchData) -> list[GameResult]:
        if stop_token.is_canceled():
            return

        statuses: list[GameServerStatus] = []
        try:
            statuses.append(GameServerStatus(**requests.get(f"http://localhost:{match_data.game_1.port}/status", timeout=DEFAULT_TIMEOUT).json()))
        except Exception as e:
            logging.error("Failed to get status for match %s: %s", match_data.game.id, e)
            exit(1)
            pass
        
        try:
            statuses.append(GameServerStatus(**requests.get(f"http://localhost:{match_data.game_2.port}/status", timeout=DEFAULT_TIMEOUT).json()))
        except Exception as e:
            logging.error("Failed to get status for match %s: %s", match_data.game.id, e)
            pass
        
        is_expired = match_data.start_time + timedelta(seconds=MATCH_EXPIRATION_TIMEOUT_MINUTES*60) < datetime.now(timezone.utc)
        if not is_expired and len(statuses) == 2 and not all(status.isOver for status in statuses):
            return

        # Delete containers
        stop_and_remove_all(match_data.game_1.game_server, match_data.game_2.game_server)
        logs = get_logs_and_remove_all(match_data.game_1.offense, match_data.game_1.defense, match_data.game_2.offense, match_data.game_2.defense)

        # Delete networks
        safe_execute(match_data.game_1.game_network.remove)
        safe_execute(match_data.game_2.game_network.remove)

        if len(statuses) != 2 or any(status.gameData is None for status in statuses):
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=to_base_64(build_simple_error("Game server error")), game_data=None)
            logging.warning("Game server crashed for match %s", match_data.game.id)
            self.results.append(game_result)
            return
        
        if is_expired:
            error_message = f"Game killed after being stuck for too long ({MATCH_EXPIRATION_TIMEOUT_MINUTES} minutes)"
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=to_base_64(build_simple_error(error_message)), game_data=None)
            logging.info("Match %s expired", match_data.game.id)
            self.results.append(game_result)
            return
        
        if any(status.gameData["errorMessage"] is not None for status in statuses):           
            error_data = build_detailed_error(match_data, statuses, logs)
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=to_base_64(error_data), game_data=None)
            self.results.append(game_result)
            logging.info("Match %s finished on error", match_data.game.id)
            return

        game_data = build_game_data(match_data, statuses, logs)

        if statuses[0].score == statuses[1].score:
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=False, team1_score=statuses[0].score, team2_score=statuses[0].score, error_data=None, game_data=to_base_64(game_data))
            self.results.append(game_result)
            logging.info("Match %s finished with tie", match_data.game.id)
            return

        winner_id = match_data.game.team1_id if statuses[0].score > statuses[1].score else match_data.game.team2_id
        game_result = GameResult(id=match_data.game.id, winner_id=winner_id, is_error=False, team1_score=statuses[0].score, team2_score=statuses[1].score, error_data=None, game_data=to_base_64(game_data))
        self.results.append(game_result)

        logging.info("Match %s finished", match_data.game.id)
