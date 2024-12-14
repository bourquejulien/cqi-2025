#!/usr/bin/env python3

import os
import socket
import boto3
import docker
import time
import boto3.session
import requests
import base64
import logging
import docker
from docker import DockerClient
from docker.models.images import Image
from docker.models.containers import Container
from docker.models.networks import Network
from dataclasses import dataclass
import numpy as np

NETWORK_BASE_NAME = 'network-game-'
GAME_SERVER_IMAGE_NAME = 'ghcr.io/bourquejulien/cqi-2024-game-server'

@dataclass
class GameStatus:
    map: np.ndarray

@dataclass
class RunnerStatus:
    is_running: bool
    is_over: bool
    score: int | None
    game_status: GameStatus | None

@dataclass
class Match:
    id: str
    team1_id: str
    team2_id: str
    image_team1: str
    image_team2: str

@dataclass
class GameResult:
    id: str
    winner_id: str | None
    is_error: bool
    team1_score: float
    team2_score: float
    error_data: str | None
    game_data: str | None


def get_available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        return port


def get_internal_key(session: boto3.session.Session) -> str:
    ecr_client = session.client(service_name="ecr", region_name="us-east-1")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']

    return username, password, registry

class Runner:
    secret: str
    base_url: str
    docker_client: DockerClient

    def __init__(self, secret: str, base_url: str, docker_client: DockerClient):
        self.secret = secret
        self.base_url = base_url + "/internal/match"
        self.docker_client = docker_client
    
    @property
    def _headers(self) -> str:
        return {'Authorization': f"{self.secret}"}

    def get_next_game(self, n: int = 1) -> Match:
        logging.info('Getting next game')
        r = requests.post(f'{self.base_url}/pop', headers=self._headers, params={'n': n})
        
        # TODO - Add error handling
        matches_data = r.json()
        matches = [Match(**match) for match in matches_data]
        return matches
        
    def cleanup(self,):
        for network in self.docker_client.networks.list():
            if network.name.startswith(NETWORK_BASE_NAME):
                for container in network.containers:
                    network.disconnect(container, force=True)
                    container.remove(force=True)
                network.remove()


    # Call on start to tell the main server to forget current running games
    def reset_games(self):
        logging.info('Resetting games')
        r = requests.post(f'{self.base_url}/reset', headers=self._headers)

    def add_result(self, result: GameResult):
        logging.info('Adding result')
        r = requests.post(f'{self.base_url}/add_result', headers=self._headers, json=result.__dict__)

def main() -> None:
    base_address = os.environ.get("SERVER_ADDRESS", "http://localhost:8000")

    # Grab secret from AWS Secrets Manager
    session = boto3.session.Session()
    secret_manager_client = session.client(service_name="secretsmanager", region_name="us-east-1")
    secret = secret_manager_client.get_secret_value(SecretId="internal_key")["SecretString"]

    # TODO - Add try catch to login
    docker_client: DockerClient = docker.from_env()
    username, password, registry = get_internal_key(session)

    docker_client.login(username=username, password=password, registry=registry)

    runner = Runner(secret=secret, base_url=base_address, docker_client=docker_client)

    # TODO - Cleanup any Containers or images on the server
    runner.cleanup()

    # Reset games in case the game runner had crashed
    runner.reset_games()

    # TODO - Grab the game_server image
    gameServerImage: Image = docker_client.images.pull(GAME_SERVER_IMAGE_NAME)

    while 1:
        # TODO - Evaluate how many games can run concurrently
        games: list[Match] = runner.get_next_game(n=1)

        for game in games:
            # Pull images
            team1_image: Image = docker_client.images.pull(game.image_team1)
            team2_image: Image = docker_client.images.pull(game.image_team2)

            # Create network
            network_name = f"{NETWORK_BASE_NAME}{game.id}"
            game_network_1: Network = docker_client.networks.create(f"{network_name}_1", driver="bridge") # TODO - Make network internal only
            game_network_2: Network = docker_client.networks.create(f"{network_name}_2", driver="bridge") # TODO - Make network internal only

            # Create containers
            # TODO - Add memory limit and CPU limit
            # TODO - Dynamically assign ports for game server

            port_1 = get_available_port()
            game_server_1: Container = docker_client.containers.create(gameServerImage, name=f"{game.id}_1", hostname="game_server", ports={"5000":port_1}, network=game_network_1.name)

            port_2 = get_available_port()
            game_server_2: Container = docker_client.containers.create(gameServerImage, name=f"{game.id}_2", hostname="game_server", ports={"5000":port_2}, network=game_network_2.name)
            
            team1Offense: Container = docker_client.containers.create(team1_image, name=f"{game.id}_{game.team1_id}_O", hostname=f"offense", network=game_network_1.name)
            team1Defense: Container = docker_client.containers.create(team1_image, name=f"{game.id}_{game.team1_id}_D", hostname=f"defense", network=game_network_2.name)
            team2Offense: Container = docker_client.containers.create(team2_image, name=f"{game.id}_{game.team2_id}_O", hostname=f"offense", network=game_network_2.name)
            team2Defense: Container = docker_client.containers.create(team2_image, name=f"{game.id}_{game.team2_id}_D", hostname=f"defense", network=game_network_1.name) 
            
            # Start the game servers
            game_server_1.start()
            game_server_2.start()

            # Start team 1 bots
            team1Offense.start()
            team1Defense.start()
            
            # Start team 2 bots
            team2Defense.start()
            team2Offense.start()

            # Start both games
            # TODO - Retry n times in case server is loaded
            # TODO - Handle failures
            time.sleep(5) # TODO - Wait for game servers and others to start
            requests.post(f'http://localhost:{port_1}/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000', "seed": game.id})
            requests.post(f'http://localhost:{port_2}/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000', "seed": game.id})

            # Wait for games to finish
            while 1:
                status1 = RunnerStatus(**requests.get(f'http://localhost:{port_1}/status').json())
                status2 = RunnerStatus(**requests.get(f'http://localhost:{port_2}/status').json())
                
                if status1.is_over and status2.is_over:
                    # Delete containers
                    game_server_1.remove(force=True)
                    game_server_2.remove(force=True)
                    team1Offense.remove(force=True)
                    team1Defense.remove(force=True)
                    team2Offense.remove(force=True)
                    team2Defense.remove(force=True)

                    # Delete networks
                    game_network_1.remove()
                    game_network_2.remove()  

                    # Add results
                    # TODO - Handle tie games
                    winner_id = game.team1_id if status1.score > status2.score else game.team2_id
                    results = GameResult(id=game.id, winner_id=winner_id, is_error=False, team1_score=status1.score, team2_score=status2.score, error_data=None, game_data=None)
                    runner.add_result(result=results)

                    break

        time.sleep(10)


if __name__ == "__main__":
    main()
