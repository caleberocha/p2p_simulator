from datetime import datetime, timedelta

from server.errors import IsNotAliveError
from flask import Flask, request

from .controllers import (
    add_files,
    get_files,
    refresh_peer,
    register_peer,
)


def create_app():
    app = Flask(__name__)

    @app.route("/register", methods=["POST"])
    def register():
        req = request.get_json(force=True)
        register_peer(req["ip"])

        return {"success": True}

    @app.route("/offerfiles", methods=["POST"])
    def offer_files():
        req = request.get_json(force=True)

        try:
            add_files(req["ip"], req["files"])
            return {"success": True}, 201
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

    @app.route("/search", methods=["POST"])
    def search_files():
        req = request.get_json(force=True)

        try:
            return get_files(req["ip"])
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

    @app.route("/iamalive", methods=["POST"])
    def alive():
        req = request.get_json(force=True)

        try:
            refresh_peer(req["ip"])
            return {"alive": True}
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

    return app