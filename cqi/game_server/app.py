#!/bin/env python3

import logging
import random
import json
import atexit
import logging
import threading

from src.game_runner import Runner

from threading import Thread
from aiohttp import web
from aiohttp.web import Response, json_response, Application, Request

game_runner: Runner
handler_thread: Thread


async def get_status(request: Request):
    status = game_runner.status()
    return json_response({"status": status})


async def run_game(request: Request):
    OFFENSE = "offense_url"
    DEFENSE = "defense_url"
    query_param = request.rel_url.query

    if OFFENSE not in query_param or DEFENSE not in query_param:
        return Response(text="Wrong parameters", status=400)

    offense_bot_url = request.rel_url.query[OFFENSE]
    defense_bot_url = request.rel_url.query[DEFENSE]
    game_runner.launch_game(offense_bot_url, defense_bot_url)

    return json_response({"status": "started"}, status=200)


async def force_end_game(request: Request):
    if not game_runner.force_end_game():
        return Response(text="No game running", status=400)

    return json_response({"status": "stopped"}, status=200)


def initialize(app: Application) -> None:
    global game_runner, handler_thread
    game_runner = Runner(app.logger)
    handler_thread = threading.Thread(target=game_runner.run, args=())
    handler_thread.start()
    atexit.register(stop)


def stop() -> None:
    print("Stopping...")
    game_runner.stop()
    handler_thread.join()


def setup_routes() -> Application:
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.router.add_get('/status', get_status)
    app.router.add_post('/run_game', run_game)
    app.router.add_post('/force_end_game', force_end_game)

    return app


def main() -> None:
    app = setup_routes()
    initialize(app)

    web.run_app(app, host="0.0.0.0", port=5000)


if __name__ == '__main__':
    main()
