from dataclasses import dataclass
import logging
import socket

import requests
from subnet_allocator import SubnetAllocator
from match_runner_helpers import DEFAULT_TIMEOUT, GAME_RUNNER_BASE_NAME, GameData
from stop_token import StopToken

import docker
from docker import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network
from docker.models.images import Image


@dataclass
class MatchStarterTeam:
    team_id: str
    image: Image


@dataclass
class MatchStarterConfig:
    max_cpu: float
    max_memory_MiB: float


def get_available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        return port

class MatchStarter:
    _offense_team: MatchStarterTeam
    _defense_team: MatchStarterTeam
    _random_id: str
    _match_id: str

    _config: MatchStarterConfig
    _docker_client: DockerClient
    _subnet_allocator: SubnetAllocator

    _error: str | None
    _game_data: GameData | None
    _is_started: bool

    def __init__(self, offense_team: MatchStarterTeam, defense_team: MatchStarterTeam, random_id: str, match_id: str, config: MatchStarterConfig, docker_client: DockerClient, subnet_allocator) -> None:
        self._offense_team = offense_team
        self._defense_team = defense_team

        self._random_id = random_id
        self._match_id = match_id

        self._config = config
        self._docker_client = docker_client
        self._subnet_allocator = subnet_allocator

        self._error = None
        self._game_data = None
        self._is_started = False

    @property
    def is_error(self) -> bool:
        return self._error is not None

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def game_data(self) -> GameData | None:
        return self._game_data

    @property
    def is_started(self) -> bool:
        return self._is_started

    def init(self, game_server_image: Image, stop_token: StopToken) -> None:
        if stop_token.is_canceled():
            return

        base_docker_id = f"{GAME_RUNNER_BASE_NAME}-{self._random_id[:8]}-{self._match_id}"
        offense_docker_id = f"{base_docker_id}-{self._offense_team.team_id}"
        defense_docker_id = f"{base_docker_id}-{self._defense_team.team_id}"

        game_network = self._create_network(base_docker_id, internal=False)
        if game_network is None:
            return

        offense_network = self._create_network(offense_docker_id, internal=True)
        if offense_network is None:
            return
        
        defense_network = self._create_network(defense_docker_id, internal=True)
        if defense_network is None:
            return

        if stop_token.is_canceled():
            return

        # Create containers
        port = get_available_port()

        # Start offense bot
        offenseBot: Container
        try:
            offenseBot = self._docker_client.containers.create(self._offense_team.image, name=offense_docker_id, hostname=f"offense", network=offense_network.name, nano_cpus=int(self._config.max_cpu * 1e9), mem_limit=f"{self._config.max_memory_MiB}m")
            offenseBot.start()
        except Exception as e:
            self._error = f"Failed to create team {self._offense_team.team_id} bots"
            logging.error(f"Failed to create offense bot: {base_docker_id}: %s", e)
            return

        # Start defense bot
        defenseBot: Container
        try:
            defenseBot = self._docker_client.containers.create(self._defense_team.image, name=defense_docker_id, hostname=f"defense", network=defense_network.name, nano_cpus=int(self._config.max_cpu * 1e9), mem_limit=f"{self._config.max_memory_MiB}m")
            defenseBot.start()
        except Exception as e:
            self._error = f"Failed to create team {self._defense_team.team_id} bots"
            logging.error(f"Failed to create defense bot: {base_docker_id}: %s", e)
            return
        
        if stop_token.is_canceled():
            return

        game_server: Container
        try:
            game_server = self._docker_client.containers.create(
                game_server_image, name=base_docker_id, hostname="game_server", ports={"5000": port}, network=game_network.name)
            
            defense_network.connect(game_server)
            offense_network.connect(game_server)

            game_server.start()
        except Exception as e:
            self._error = "Failed to create game server"
            logging.error(f"Failed to create game server for: {base_docker_id}: %s", e)
            return

        if stop_token.is_canceled():
            return

        self._game_data = GameData(port=port,
                                   game_networks=[game_network, offense_network, defense_network],
                                   game_server=game_server,
                                   offense=offenseBot,
                                   defense=defenseBot)

    def start(self) -> None:
        if self.game_data is None:
            return

        if self.is_started:
            return

        try:
            response = requests.post(f"http://localhost:{self.game_data.port}/run_game", timeout=DEFAULT_TIMEOUT, params={
                                     "offense_url": f"http://offense:5000", "defense_url": f"http://defense:5000", "seed": self._random_id})
            response.raise_for_status()

            self._is_started = True
        except:
            pass
    
    def _create_network(self, name: str, internal: bool) -> Network | None:
        ipam = docker.types.IPAMConfig(
            driver="default",
            pool_configs=[docker.types.IPAMPool(subnet=self._subnet_allocator.allocate())]
        )
        
        try:
            return self._docker_client.networks.create(name, driver="bridge", internal=internal, ipam=ipam)
        except Exception as e:
            logging.error(f"Failed to create network: {name}: {e}")
            self._error = "Failed to create network"
            return None
