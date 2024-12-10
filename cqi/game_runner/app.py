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

def get_next_game(secret: str, n: int = 1) -> Match:
    logging.info('Getting next game')
    r = requests.post('http://localhost:8000/api/internal/match/pop', headers={'Authorization': f'{secret}'}, params={'n': n})
    
    # TODO - Add error handling
    matches_data = r.json()
    matches = [Match(**match) for match in matches_data]
    return matches
    
def cleanup(client: DockerClient):
    for network in client.networks.list():
        if network.name.startswith(NETWORK_BASE_NAME):
            for container in network.containers:
                network.disconnect(container, force=True)
                container.remove(force=True)
            network.remove()


# Call on start to tell the main server to forget current running games
def reset_games(secret: str):
    logging.info('Resetting games')
    r = requests.post('http://localhost:8000/api/internal/match/reset', headers={'Authorization': f'{secret}'})

def add_result(secret: str, result: GameResult):
    logging.info('Adding result')
    r = requests.post('http://localhost:8000/api/internal/match/add_result', headers={'Authorization': f'{secret}'}, json=result.__dict__)

def main() -> None:
    # Grab secret from AWS Secrets Manager
    session = boto3.session.Session()
    secret_manager_client = session.client(service_name="secretsmanager", region_name="us-east-1")
    secret = secret_manager_client.get_secret_value(SecretId='internal_key')["SecretString"]

    # TODO - Add try catch to login
    docker_client: DockerClient = docker.from_env()
    ecr_client = session.client(service_name="ecr", region_name="us-east-1")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']
    docker_client.login(username=username, password=password, registry=registry)

    # TODO - Cleanup any Containers or images on the server
    cleanup(docker_client)

    # Reset games in case the game runner had crashed
    reset_games(secret)

    # TODO - Grab the game_server image
    GAME_SERVER_IMAGE: Image = docker_client.images.pull(GAME_SERVER_IMAGE_NAME)

    while 1:
        # TODO - Evaluate how many games can run concurrently
        games: list[Match] = get_next_game(secret=secret, n=1)

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
            game_server_1: Container = docker_client.containers.create(GAME_SERVER_IMAGE, name=f"{game.id}_1", hostname="game_server", ports={"5000":"5000"}, network=game_network_1.name)
            game_server_2: Container = docker_client.containers.create(GAME_SERVER_IMAGE, name=f"{game.id}_2", hostname="game_server", ports={"5000":"5001"}, network=game_network_2.name)
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
            requests.post(f'http://localhost:5000/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000', "seed": game.id})
            requests.post(f'http://localhost:5001/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000', "seed": game.id})

            # Wait for games to finish
            while 1:
                status1 = RunnerStatus(**requests.get(f'http://localhost:5000/status').json())
                status2 = RunnerStatus(**requests.get(f'http://localhost:5001/status').json())
                
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
                    add_result(secret=secret, result=results)

                    break

        time.sleep(10)


if __name__ == "__main__":
    main()