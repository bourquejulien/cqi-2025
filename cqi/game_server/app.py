#!/bin/env python3

import logging
import random
import json

import requests

from flask import Flask, Response, request
from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
app: Flask = Flask(__name__)
cache.init_app(app)

START_ENDPOINT = "/start"
OFFENSE_ENDPOINT = "/offense"
DEFENSE_ENDPOINT = "/defense"
END_ENDPOINT = "/end_game"

class GameHandler:
    bot1_url: str
    bot2_url: str

    def __init__(self, bot1_url: str, bot2_url: str) -> None:
        self.bot1_url = bot1_url
        self.bot2_url = bot2_url

    def launch_game(self):
        
        requests.post(self.bot1_url + START_ENDPOINT, json={"is_offense": True})
        requests.post(self.bot2_url + START_ENDPOINT, json={"is_offense": False})

        response1 = requests.post(self.bot1_url + OFFENSE_ENDPOINT, {})
        response2 = requests.post(self.bot2_url + DEFENSE_ENDPOINT, {})

        requests.post(self.bot1_url + END_ENDPOINT, {})
        requests.post(self.bot2_url + END_ENDPOINT, {})

@app.route("/status", methods=["GET"])
def get_status():
    
    return {"status": "🤨"}

@app.route("/run_game", methods=["POST"])
def run_game():

    bot1_url = "http://localhost:5000"
    bot2_url = "http://localhost:5001"

    handler = GameHandler(bot1_url, bot2_url)
    handler.launch_game()
    
    return Response(
            response={
                "status": "started"
            },
            status=200
        )
    
def start_gunicorn():
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    return app

if __name__ == "__main__":
    app.run("0.0.0.0", 8000, debug=True)
