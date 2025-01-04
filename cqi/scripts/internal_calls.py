#!/bin/env python3

import sys
import os
import requests
import readline
import boto3

LOCAL_URL = "http://localhost:8000"
PROD_URL = "https://server.cqiprog.info"
STRIP_CHARS = " \t'\""

def get_secret(secret_name: str) -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name="us-east-1"
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    return get_secret_value_response["SecretString"]


class InternalAPI:
    secret: str
    base_url: str

    def __init__(self, secret: str, base_url: str):
        self.secret = secret
        self.base_url = base_url + "/internal"

    @property
    def _headers(self) -> str:
        return {"Authorization": self.secret}
    
    def get_settings(self) -> dict:
        result = requests.get(f"{self.base_url}/settings", timeout=5, headers=self._headers)
        return result.json()

    def update_settings(self, settings: dict) -> None:
        result = requests.post(f"{self.base_url}/settings", timeout=5, headers=self._headers, json=settings)
        result.raise_for_status()
    
    def set_autoplay(self, is_enabled: bool) -> None:
        result = requests.post(f"{self.base_url}/autoplay?enabled={is_enabled}", timeout=5, headers=self._headers)
        result.raise_for_status()
    
    def force_queue_match(self, team1_id: str, team2_id: str) -> None:
        result = requests.post(f"{self.base_url}/force_queue?team1_id={team1_id}&team2_id={team2_id}", timeout=5, headers=self._headers)
        
        if not result.ok:
            print("Failed to force queue match: " + result.text)
            return

def print_settings(settings: dict) -> None:
    BORDER = "\u001B[35m" + "~"*40 + "\u001B[0m"
    ARROW = "\u001B[32m=>\u001B[0m"
    print(BORDER)
    for key, value in settings.items():
        print(f"{ARROW} {key}= {value}")
    print(BORDER)

def update_settings(api: InternalAPI) -> int:
    settings = api.get_settings()

    print_settings(settings)

    values_to_update = input("Enter values to update (key1=value1,key2=value2,...): ")
    updated_settings = {}
    for values in values_to_update.strip("\n").split(","):
        if "=" not in values:
            continue

        key, value = values.split("=")
        key = key.strip(STRIP_CHARS)
        value = value.strip(STRIP_CHARS)

        if key not in settings:
            print(f"Key {key} not found in settings")
            continue

        updated_settings[key] = value
    
    if len(updated_settings) == 0:
        return 0

    print("Updated values:")
    print_settings(updated_settings)

    update = input("Update settings? (y/n): ")

    if update.lower() == "y":
        api.update_settings(updated_settings)
        print("Settings updated")
    
    print("Current settings:")
    print_settings(api.get_settings())

    return 0

def set_autoplay(api: InternalAPI) -> int:
    autoplay = input("Enter autoplay (true/false): ")

    if len(autoplay) == 0:
        return 0

    if autoplay.lower()[0] not in ["t", "f"]:
        print("Invalid value")
        return 1

    api.set_autoplay(autoplay.lower()[0] == "t")

    return 0


def force_queue_match(api: InternalAPI) -> int:
    team1_id = input("Enter team1 id: ")
    team2_id = input("Enter team2 id: ")

    if len(team1_id) == 0 or len(team2_id) == 0:
        return 0
    
    api.force_queue_match(team1_id, team2_id)
    return 0

def is_running_on_local_host() -> bool:
    try:
        response = requests.get(LOCAL_URL + "/health", timeout=2)
        response.raise_for_status()
        return True
    except:
        return False

def main() -> int:
    base_url = LOCAL_URL if os.environ.get("ENVIRON") == "local" or is_running_on_local_host() else PROD_URL
    secret = get_secret("internal_key")

    print("Using base url:", base_url)

    api = InternalAPI(secret=secret, base_url=base_url)

    modes = [
        ("Exit", lambda *_: 0),
        ("Update Settings", update_settings),
        ("Set Autoplay", set_autoplay),
        ("Force Queue Match", force_queue_match)
    ]

    mode = input(f"Enter mode [{", ".join(f'{mode[0]}({i})' for i, mode in enumerate(modes))}]: ")

    if not mode.isdigit() or int(mode) >= len(modes):
        print("Invalid mode")
        return 1

    return modes[int(mode)][1](api)

if __name__ == "__main__":
    sys.exit(main())
