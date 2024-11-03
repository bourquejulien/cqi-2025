#!/bin/env python3

import logging
import os
import logging

from aiohttp import web
from aiohttp.web import Response, json_response, Application, Request

from src.offense_game import DumbOffenseBot
from src.defense_game import RandomDefenseBot

ENV_PORT = "PORT"
ENV_MODE = "MODE"
DEFAULT_PORT = 5001

should_play_offense = True
dumb_bot = DumbOffenseBot()
random_defense = RandomDefenseBot()

def play_offense(payload: dict) -> Response:
    data = payload["map"]
    move = dumb_bot.play(data)

    if move is None:
        return Response(
            text="Unable to play",
            status=400
        )

    return json_response({"move": move.value})


def play_defense(payload: dict) -> Response:
    data = payload["map"]
    move, position = random_defense.play(data)
    logging.info(payload, move)
    if move is None or position is None:
        return Response(
            text="Unable to play",
            status=400
        )

    return json_response({"x": position.x, "y": position.y, "element": move.value})

async def start(request: Request):
    global should_play_offense
    data = request.json
    should_play_offense = data["is_offense"]

    return Response(
        text="OK",
        status=200
    )


async def next_move(request: Request):
    payload = await request.json()

    if should_play_offense:
        return play_offense(payload)
    else:
        return play_defense(payload)


async def end_game(request: Request):
    return Response(
        text="OK",
        status=200
    )


def setup_web_server(is_debug: bool) -> Application:
    extra_format = " %(module)s-%(funcName)s:" if is_debug else ":"
    logging.basicConfig(level=logging.DEBUG if is_debug else logging.INFO,
                        format=f"%(asctime)s %(levelname)s{
                            extra_format} %(message)s",
                        datefmt="%d-%m-%Y %H:%M:%S"
                        )

    app = web.Application(logger=logging.getLogger())

    app.router.add_get("/start", start)
    app.router.add_post("/next_move", next_move)
    app.router.add_post("/end_game", end_game)

    return app


def main() -> None:
    port = int(os.environ[ENV_PORT]) \
        if ENV_PORT in os.environ \
        else DEFAULT_PORT
    is_debug = ENV_MODE not in os.environ or os.environ[ENV_MODE] == "debug"

    app = setup_web_server(is_debug=is_debug)

    host = "0.0.0.0"
    app.logger.info("Starting bot on %s", f"{host}:{port}")
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
