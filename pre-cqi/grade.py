#!/bin/env python3

'''
Dependencies:
- Docker SDK for Python

Installation:
- pip install docker
'''

import sys
import requests
import time
import docker

from docker import DockerClient
from docker.models.networks import Network
from docker.models.containers import Container

GRADING_IMAGE_NAME = "brqu/pre-cqi-prog-2025:latest"
RUN_COUNT = 10
GAME_TIMEOUT = 30

class Grader:
    _client: DockerClient
    _team_image_name: str
    _grader_port: int
    _network_name: str
    _grading_container_name: str

    _network: Network | None
    _grading_container: Container | None
    _team_container: Container | None

    def __init__(self, client: DockerClient, team_image_name: str) -> None:
        self._client = client
        self._team_image_name = team_image_name
        self._grader_port = 7869
        self._grading_container = None
        self._team_container = None
        self._network_name = "grader_network"
        self._grading_container_name = "grader"

    def prepare(self):
        self._client.images.pull(GRADING_IMAGE_NAME)
        self._client.images.pull(self._team_image_name)

        for container in self._client.containers.list(all=True):
            if container.name == self._grading_container_name:
                container.remove(force=True)
                break

        for network in self._client.networks.list():
            if network.name == self._network_name:
                for container in network.containers:
                    network.disconnect(container, force=True)
                network.remove()
                break

        self._network = self._client.networks.create(self._network_name, driver="bridge")
        self._grading_container = self._client.containers.run(GRADING_IMAGE_NAME, name=self._grading_container_name, detach=True, network=self._network.name, hostname=self._network_name, ports={"5000": self._grader_port})

        time.sleep(5)
        response = requests.get(f"http://localhost:{self._grader_port}/status")

        if not response.ok and not response.content.startswith(b"No game available"):
            raise Exception("Failed to connect to grading server")
    
    def stop(self):
        self.reset()
        self._grading_container.stop(timeout=5)
        self._network.remove()

    def grade(self) -> int | None:
        self._team_container = self._client.containers.run(self._team_image_name, detach=True, network=self._network.name, hostname=self._network_name, command="grade:5000")
        self._team_container.wait(timeout=GAME_TIMEOUT)

        response = requests.get(f"http://localhost:{self._grader_port}/status")

        if not response.ok:
            print("No game status available")
            return None

        game_response = response.json()
        if not game_response["game_over"]:
            return None
        
        return game_response["score"]

    def reset(self):
        if self._team_container is None:
            return

        self._team_container.reload()
        if self._team_container.status == "running":
            print("Container not correctly stopped")
        
        self._team_container.remove(force=True)
        self._team_container = None


def main():
    client = docker.from_env()

    team_image_name: str
    if len(sys.argv) < 2:
        print("Input team image name:")
        team_image_name = input()
    else:
        team_image_name = sys.argv[1]

    grader = Grader(client, team_image_name)
    grader.prepare()

    total_score = 0
    for i in range(RUN_COUNT):
        score = grader.grade()
        grader.reset()

        formatted_score = "RUN FAILED"
        if score is not None:
            total_score += score
            formatted_score = score

        print(f"Score un run {i+1}: {formatted_score}")
    
    print(f"Average score after {RUN_COUNT} runs: {total_score/RUN_COUNT}")

    grader.stop()

if __name__ == "__main__":
    main()
