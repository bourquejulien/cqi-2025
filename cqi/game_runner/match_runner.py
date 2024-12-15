from dataclasses import dataclass
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
from interfaces import GameResult, Match, RunnerStatus

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
    
GAME_RUNNER_BASE_NAME = "game-runner-managed"

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
        start_string = GAME_RUNNER_BASE_NAME + "-" + (id or "")

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
        self.cleanup(match.id)
        logging.error("Failed to run match %s: %s", match.id, error)

        # TODO - Add error data
        self.results.append(GameResult(id=match.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=None, game_data=None))

    def _run_match(self, stop_token: StopToken, match: Match) -> None:
        if stop_token.is_canceled():
            return

        # Pull images
        team1_image: Image = self.docker_client.images.pull(match.image_team1)
        team2_image: Image = self.docker_client.images.pull(match.image_team2)

        id = match.id[:8]

        # Create network
        base_docker_id = f"{GAME_RUNNER_BASE_NAME}-{id}"

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
            self._handle_error(match, "Failed to create team 1 bots")
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
            self._handle_error(match, "Failed to create team 2 bots")
            return
        
        if stop_token.is_canceled():
            return

        # Start both games
        game_1_started = False
        game_2_started = False

        for _ in range(5):
            time.sleep(1)

            if not game_1_started:
                r1 = requests.post(f"http://localhost:{port_1}/run_game", params={"offense_url": f"http://offense:5000", "defense_url": f"http://defense:5000", "seed": match.id})
                game_1_started = r1.ok
            
            if not game_2_started:
                r2 = requests.post(f"http://localhost:{port_2}/run_game", params={"offense_url": f"http://offense:5000", "defense_url": f"http://defense:5000", "seed": match.id})
                game_2_started = r2.ok

        if not game_1_started or not game_2_started:
            self._handle_error(match, "Failed to start games")
            return        

        game_data_1 = GameData(port=port_1, game_network=game_network_1, game_server=game_server_1, offense=team1Offense, defense=team1Defense)
        game_data_2 = GameData(port=port_2, game_network=game_network_2, game_server=game_server_2, offense=team2Offense, defense=team2Defense)
        match_data = MatchData(game=match, start_time=datetime.now(timezone.utc), game_1=game_data_1, game_2=game_data_2)

        self.current_matches[match_data.game.id] = match_data

    def get_match_results(self, stop_token: StopToken, match_data: MatchData) -> list[GameResult]:
        # Wait for games to finish

        if stop_token.is_canceled():
            return

        status1: RunnerStatus
        status2: RunnerStatus
        try:
            status1 = RunnerStatus(**requests.get(f"http://localhost:{match_data.game_1.port}/status").json())
        except:
            status1 = None
        
        try:
            status2 = RunnerStatus(**requests.get(f"http://localhost:{match_data.game_2.port}/status").json())
        except:
            status2 = None
        
        is_expired = match_data.start_time + timedelta(seconds=180) < datetime.now(timezone.utc)
        if not is_expired and status1 is not None and status2 is not None and not status1.is_over or not status2.is_over:
            return

        # Delete containers
        # TODO - Add remove retries
        safe_execute(match_data.game_1.game_server.remove, force=True)
        safe_execute(match_data.game_2.game_server.remove, force=True)
        safe_execute(match_data.game_1.offense.remove, force=True)
        safe_execute(match_data.game_1.defense.remove, force=True)
        safe_execute(match_data.game_2.offense.remove, force=True)
        safe_execute(match_data.game_2.defense.remove, force=True)

        # Delete networks
        # TODO - Add remove retries
        safe_execute(match_data.game_1.game_network.remove)
        safe_execute(match_data.game_2.game_network.remove)

        if is_expired:
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=None, game_data=None)
            logging.info("Match %s expired", match_data.game.id)
            self.results.append(game_result)
            return

        if status1 is None or status2 is None:
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=True, team1_score=None, team2_score=None, error_data=None, game_data=None)
            logging.warning("Game server crashed for match %s", match_data.game.id)
            self.results.append(game_result)
            return

        # TODO Add error data and game data
        if status1.score == status2.score:
            game_result = GameResult(id=match_data.game.id, winner_id=None, is_error=False, team1_score=status1.score, team2_score=status2.score, error_data=None, game_data=None)
            self.results.append(game_result)
            return

        winner_id = match_data.game.team1_id if status1.score > status2.score else match_data.game.team2_id
        game_result = GameResult(id=match_data.game.id, winner_id=winner_id, is_error=False, team1_score=status1.score, team2_score=status2.score, error_data=None, game_data=None)
        self.results.append(game_result)

        logging.info("Match %s finished", match_data.game.id)
