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

@dataclass
class GameStatus:
    map: list

@dataclass
class RunnerStatus:
    is_running: bool
    is_over: bool
    game_status: GameStatus | None

@dataclass
class Match:
    Id: str
    Team1Id: str
    Team2Id: str
    ImageTeam1: str
    ImageTeam2: str

@dataclass
class GameResult:
    Id: str
    WinnerId: str | None
    IsError: bool
    Team1Score: float
    Team2Score: float
    ErrorData: str | None
    GameData: str | None

def get_next_game(secret: str, n: int = 1) -> Match:
    logging.info('Getting next game')
    r = requests.post('http://localhost:8000/api/internal/match/pop', headers={'Authorization': f'{secret}'}, params={'n': n})
    
    # TODO - Add error handling
    return list(Match(**r.json()))
    

# Call on start to tell the main server to forget current running games
def reset_games(secret: str):
    logging.info('Resetting games')
    r = requests.post('http://localhost:8000/api/internal/match/reset', headers={'Authorization': f'{secret}'})

def add_result(secret: str, result: GameResult):
    logging.info('Adding result')
    r = requests.post('http://localhost:8000/api/internal/match/add_result', headers={'Authorization': f'{secret}'}, json=result.__dict__)

def main() -> None:
    # Grab secret from AWS Secrets Manager
    session = boto3.session.Session(profile_name='cqi') # TODO - Production can use default profile
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

    # TODO - Grab the game_server image
    GAME_SERVER_IMAGE_NAME = 'ghcr.io/bourquejulien/cqi-2024-game-server'
    GAME_SERVER_IMAGE: Image = docker_client.images.pull(GAME_SERVER_IMAGE_NAME)

    while 1:
        # TODO - Evaluate how many games can run concurrently
        games: list[Match] = get_next_game(secret=secret, n=1)

        for game in games:
            # Pull images
            docker_client.images.pull(game.ImageTeam1)
            docker_client.images.pull(game.ImageTeam2)

            # Create containers
            # TODO - Add memory limit and CPU limit
            # TODO - Dynamically assign ports for game server
            game_server_1: Container = docker_client.containers.create(GAME_SERVER_IMAGE_NAME, name=f"{game.Id}_1", hostname="game_server", ports={"5000":"5000"})
            game_server_2: Container = docker_client.containers.create(GAME_SERVER_IMAGE_NAME, name=f"{game.Id}_2", hostname="game_server", ports={"5001":"5000"})
            team1Offense: Container = docker_client.containers.create(game.ImageTeam1, name=f"{game.Id}_{game.Team1Id}_O", hostname=f"offense")
            team1Defense: Container = docker_client.containers.create(game.ImageTeam1, name=f"{game.Id}_{game.Team1Id}_D", hostname=f"defense")
            team2Offense: Container = docker_client.containers.create(game.ImageTeam2, name=f"{game.Id}_{game.Team2Id}_O", hostname=f"offense")
            team2Defense: Container = docker_client.containers.create(game.ImageTeam2, name=f"{game.Id}_{game.Team2Id}_D", hostname=f"defense")

            # Create network
            network_name = f"network_{game.Id}"
            game_network_1: Network = docker_client.networks.create(f"{network_name}_1", driver="bridge", internal=True)
            game_network_2: Network = docker_client.networks.create(f"{network_name}_2", driver="bridge", internal=True)
            
            # Start game 1
            team1Offense.start(network=game_network_1.name)
            team2Defense.start(network=game_network_1.name)
            game_server_1.start(network=game_network_1.name)
            requests.post(f'http://localhost:5000/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000'})


            # Start game 2
            team1Defense.start(network=game_network_2.name)
            team2Offense.start(network=game_network_2.name)
            game_server_2.start(network=game_network_2.name)
            requests.post(f'http://localhost:5000/run_game', params={'offense_url': f'http://offense:5000', 'defense_url': f'http://defense:5000'})

            # Wait for games to finish
            while 1:
                status1 = RunnerStatus(**requests.get(f'http://localhost:5000/status').json())
                status2 = RunnerStatus(**requests.get(f'http://localhost:5001/status').json())

                if status1.is_over and status2.is_over:
                    break

        time.sleep(1)


if __name__ == "__main__":
    main()