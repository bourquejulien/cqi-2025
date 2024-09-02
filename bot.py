#!/bin/env python3

from dataclasses import dataclass
from flask import (
    Flask, 
    jsonify
)

@dataclass
class StartGameResponse:
    isStarting: bool

@dataclass
class SendMoveRequest:
    move: ...

@dataclass
class SendMoveResponse:
    newMap: ...

def generateServer():
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return "ok ✅"
    
    @app.route('/start_game')
    def start_game():
        start_game_response = StartGameResponse()
        return jsonify(dict(start_game_response))
    
    @app.route('/send_move')
    def send_move():
        send_move_response = StartGameResponse()
        return jsonify(dict(send_move_response))
    
    return app


if __name__ == "__main__":
    app = generateServer()
    app.run(debug=True)
