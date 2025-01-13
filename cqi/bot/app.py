#!/bin/env python3

import logging
import os
import logging

from aiohttp import web
from aiohttp.web import Response, json_response, Application, Request

from src.offense.shortest_path_bot import ShortestPathBot
from src.offense.offense_bot import DumbOffenseBot
from src.defense.bots import RandomDefenseBot, BlockerDefenseBot
from src.defense.defense import Defense

from flag import ENFORCE_EASY

ENV_PORT = "PORT"
ENV_MODE = "MODE"
ENV_LEVEL = "BOT_LEVEL"
DEFAULT_PORT = 5001

should_play_offense = True
offense_bot: DumbOffenseBot | ShortestPathBot | None = None
defense: Defense | None = None
level: str = ""

def play_offense(payload: dict) -> Response:
    data = payload["map"]

    logging.info(f"Playing offense {offense_bot.__class__.__name__}")
    move = offense_bot.play(data)
    logging.debug("Moved played: %s", move)

    if move is None:
        return Response(
            text="Unable to play",
            status=400
        )

    return json_response({"move": move.value})


def play_defense(payload: dict) -> Response:
    data = payload["map"]
    logging.debug(f"Playing defense {defense.bot.__class__.__name__}")
    result = defense.play(data)
    if result is None:
        return Response(
            text="Unable to play",
            status=400
        )

    move, position = result
    logging.debug("%s, %s", move, position)

    return json_response({"x": position.x, "y": position.y, "element": move.value})


async def start(request: Request):
    global should_play_offense, offense_bot, defense
    logging.warning("Starting game - %s bot", level)

    data = await request.json()
    should_play_offense = data["is_offense"]

    if should_play_offense:
        if level == "easy":
            offense_bot = DumbOffenseBot()
        else:
            offense_bot = ShortestPathBot()
    else:
        n_walls = data["n_walls"]
        if level == "easy":
            defense = Defense(RandomDefenseBot())
        else:
            defense = Defense(BlockerDefenseBot(n_walls=n_walls))

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
    logging.basicConfig(level=logging.DEBUG if is_debug else logging.WARNING,
                        format=f"%(asctime)s %(levelname)s{
                            extra_format} %(message)s",
                        datefmt="%d-%m-%Y %H:%M:%S"
                        )

    app = web.Application(logger=logging.getLogger())

    app.router.add_post("/start", start)
    app.router.add_post("/next_move", next_move)
    app.router.add_post("/end_game", end_game)

    return app


def main() -> None:
    port = int(os.environ[ENV_PORT]) \
        if ENV_PORT in os.environ \
        else DEFAULT_PORT
    is_debug = ENV_MODE not in os.environ or os.environ[ENV_MODE] == "debug"

    global level
    level = os.environ[ENV_LEVEL] if ENV_LEVEL in os.environ else "medium"

    if ENFORCE_EASY:
        level = "easy"

    app = setup_web_server(is_debug=is_debug)

    host = "0.0.0.0"
    app.logger.info("Starting bot on %s", f"{host}:{port}")
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
