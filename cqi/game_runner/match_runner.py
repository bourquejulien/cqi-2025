import logging
import time
from datetime import datetime, timezone, timedelta

from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image

import requests

from match_starter import MatchStarter, MatchStarterConfig, MatchStarterTeam
from stop_token import StopToken
from interfaces import GameResult, Match, GameServerStatus

from match_runner_helpers import *

MATCH_EXPIRATION_TIMEOUT_MINUTES = 5

@dataclass
class MatchData:
    game: Match
    start_time: float
    game_1: GameData
    game_2: GameData

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

class MatchRunner:
    game_server_image: Image
    docker_client: DockerClient
    match_starter_config: MatchStarterConfig

    current_matches: dict[str, MatchData]
    results: list[GameResult]

    def __init__(self, game_server_image: Image, docker_client: DockerClient) -> None:
        self.game_server_image = game_server_image
        self.docker_client = docker_client
        self.match_starter_config = MatchStarterConfig(max_cpu=get_cpu_per_container(), max_memory_MiB=get_memory_per_container())

        logging.info("Container limits: CPU %s, Memory %s MiB", self.match_starter_config.max_cpu, self.match_starter_config.max_memory_MiB)

        self.current_matches = {}
        self.results = []
    
    @property
    def currently_running(self) -> int:
        return len(self.current_matches)
    
    def run_matches(self, stop_token: StopToken, matches: list[Match]) -> None:
        game_server_image = self._pull_image(self.game_server_image.tags[0])
        if game_server_image is None:
            logging.error("Failed to pull game server image")
        else:
            self.game_server_image = game_server_image

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

    def _pull_image(self, image: str) -> Image | None:
        try:
            return self.docker_client.images.pull(image)
        except:
            return None

    def _run_match(self, stop_token: StopToken, match: Match) -> None:
        if stop_token.is_canceled():
            return
        
        team1_image = self._pull_image(match.image_team1)
        if team1_image is None:
            self._handle_error(match, f"Failed to pull {match.image_team1} image")
            return

        team2_image = self._pull_image(match.image_team2)
        if team2_image is None:
            self._handle_error(match, f"Failed to pull {match.image_team2} image")
            return

        if stop_token.is_canceled():
            return
        
        team1 = MatchStarterTeam(team_id=match.team1_id, image=team1_image)
        team2 = MatchStarterTeam(team_id=match.team2_id, image=team2_image)
        
        match1 = MatchStarter(team1, team2, match.id, "1", self.match_starter_config, self.docker_client)
        match2 = MatchStarter(team2, team1, match.id, "2", self.match_starter_config, self.docker_client)

        match1.init(self.game_server_image, stop_token)
        if match1.is_error:
            self._handle_error(match, match1.error)
            return

        match2.init(self.game_server_image, stop_token)
        if match2.is_error:
            self._handle_error(match, match2.error)
            return
        
        if stop_token.is_canceled():
            return

        # Start both games
        for _ in range(5):
            if match1.is_started and match2.is_started:
                break
            
            match1.start()
            match2.start()
            time.sleep(1)

        if not match1.is_started or not match2.is_started:
            self._handle_error(match, "Failed to start games")
            return

        match_data = MatchData(game=match, start_time=datetime.now(timezone.utc), game_1=match1.game_data, game_2=match2.game_data)
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
        for network in match_data.game_1.game_networks:
            safe_execute(network.remove)

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
