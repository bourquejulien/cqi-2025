#!/bin/env python3

from flask import Flask, request, Response

app: Flask = Flask(__name__)

@app.route("/start", methods=["POST"])
def start():
    data = request.json
    if data['is_offense'] == True:
        offense()
    else:
        defense()

    return Response(
            response="OK",
            status=200
        )

@app.route("/offense", methods=["POST"])
def offense():
    return Response(
            response="OK",
            status=200
        )

@app.route("/defense", methods=["POST"])
def defense():
    return Response(
            response="OK",
            status=200
        )

@app.route("/end_game", methods=["POST"])
def end_game():
    return Response(
            response="OK",
            status=200
        )

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
