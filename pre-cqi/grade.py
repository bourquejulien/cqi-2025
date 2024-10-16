#!/bin/env python3

'''
Dependencies:
- Docker SDK for Python

Installation:
- pip install docker
'''

import signal
import time
import requests
import sys
import socket
import uuid
import subprocess


def imports() -> None:
    global docker, DockerClient, Container, Network
    import docker
    from docker import DockerClient
    from docker.models.containers import Container
    from docker.models.networks import Network


def install_dependencies(dependencies: list[str]) -> bool:
    print(f"Failed to load dependencies: {dependencies}")
    should_install = input(
        "Do you want to install them in the current environnement (Y, N)? \n").lower().startswith("y")
    if not should_install:
        return False

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", " ".join(dependencies)])
    except:
        print("Unable to install dependencies, did you install pip (https://pip.pypa.io/en/stable/installation/)?")
        return False

    return True


try:
    imports()
except:
    if not install_dependencies(["docker"]):
        print("Install the required dependencies to continue")
        exit(1)
    imports()


GRADING_IMAGE_NAME = "brqu/pre-cqi-prog-2025:latest"
GRADER_NAME_BASE = "grader"
TEAM_NAME_BASE = "team"
NETWORK_NAME_BASE = "grader_network"
RUN_COUNT = 10
GAME_TIMEOUT = 30
STOP_TIMEOUT = 5


should_stop = False


def signal_handler(sig, frame) -> None:
    global should_stop
    print("Stopping...")
    should_stop = True


def get_available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        return port


class Grader:
    _client: DockerClient
    _team_image_name: str
    _grader_port: int
    _network_name: str
    _grading_container_name: str
    _team_container_name: str

    _network: Network | None
    _grading_container: Container | None
    _team_container: Container | None

    def __init__(self, client: DockerClient, team_image_name: str) -> None:
        run_id = uuid.uuid4().hex[:5]

        self._client = client
        self._team_image_name = team_image_name
        self._grader_port = get_available_port()
        self._grading_container = None
        self._team_container = None
        self._network_name = f"{NETWORK_NAME_BASE}_{run_id}"
        self._grading_container_name = f"{GRADER_NAME_BASE}_{run_id}"
        self._team_container_name = f"{TEAM_NAME_BASE}_{run_id}"

    def prepare(self) -> bool:
        print("Pulling containers...")
        self._client.images.pull(GRADING_IMAGE_NAME)

        try:
            self._client.images.pull(self._team_image_name)
        except Exception as e:
            print(f"Unable to pull {self._team_image_name}: {e}")
            return False

        self._cleanup()

        print("Starting grader...")
        self._network = self._client.networks.create(
            self._network_name, driver="bridge")
        self._grading_container = self._client.containers.run(GRADING_IMAGE_NAME, name=self._grading_container_name,
                                                              detach=True, network=self._network.name, hostname=self._grading_container_name, ports={"5000": self._grader_port})

        time.sleep(STOP_TIMEOUT)
        response = requests.get(f"http://localhost:{self._grader_port}/status")

        if not response.ok and not response.content.startswith(b"No game available"):
            raise Exception("Failed to connect to grading server")

        print("Grader started successfully")
        return True

    def _cleanup(self):
        container: Container
        for container in self._client.containers.list(all=True):
            if container.name.startswith((GRADER_NAME_BASE, TEAM_NAME_BASE)):
                container.remove(force=True)

        for network in self._client.networks.list():
            if network.name.startswith(NETWORK_NAME_BASE):
                for container in network.containers:
                    network.disconnect(container, force=True)
                network.remove()

    def stop(self) -> None:
        self.reset()
        self._grading_container.stop(timeout=STOP_TIMEOUT)
        self._network.remove()

    def grade(self) -> int | None:
        self._team_container = self._client.containers.run(
            self._team_image_name, detach=True, network=self._network.name, command=f"{self._grading_container_name}:5000")

        try:
            self._team_container.wait(timeout=GAME_TIMEOUT)
        except:
            print("Bot timed out")
            return None

        try:
            response = requests.get(
                f"http://localhost:{self._grader_port}/status")
        except:
            print("Unable to access grader")
            return None

        if not response.ok:
            print("No game status available")
            return None

        game_response = response.json()
        if not game_response["game_over"]:
            return None

        return game_response["score"]

    def reset(self) -> None:
        if self._team_container is None:
            return

        self._team_container.reload()
        if self._team_container.status == "running":
            print("Container not correctly stopped")

        self._team_container.remove(force=True)
        self._team_container = None


def main() -> None:
    client: DockerClient

    try:
        client = docker.from_env()
    except:
        noob_instructions = \
            "Unable to access Docker. Is docker installed and running (can you run \"docker run hello-world\")?\n" \
            "If you are on Linux and Docker is install, you probably need to allow Docker to be accessed from your user (https://docs.docker.com/engine/install/linux-postinstall/). You can also run this script as root, but thats NOT RECOMMENDED.\n" \
            "Else you need to install Docker: https://docs.docker.com/get-started/get-docker/.\n" \
            "Note: If you are using Windows, the WSL 2 Docker installation method is preferred."
        print(noob_instructions)
        exit(1)

    team_image_name: str
    if len(sys.argv) < 2:
        print("Input team image name:")
        team_image_name = input()
    else:
        team_image_name = sys.argv[1]

    signal.signal(signal.SIGINT, signal_handler)
    grader = Grader(client, team_image_name)
    if not grader.prepare():
        exit(1)

    total_score = 0
    for i in range(RUN_COUNT):
        if should_stop:
            break

        score = grader.grade()
        grader.reset()

        formatted_score = "RUN FAILED"
        if score is not None:
            total_score += score
            formatted_score = score

        print(f"Score run {i+1}: {formatted_score}")

    print(f"Average score after {RUN_COUNT} runs: {total_score/RUN_COUNT}")

    grader.stop()


if __name__ == "__main__":
    main()
