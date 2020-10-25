from datetime import datetime, timedelta

from server.errors import InvalidRequestError, IsNotAliveError
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
        try:
            listen_port = req["listen_port"]
        except KeyError as e:
            return {"error": f"{e} missing"}, 400

        register_peer(request.remote_addr, listen_port)

        return {"success": True}

    @app.route("/offerfiles", methods=["POST"])
    def offer_files():
        req = request.get_json(force=True)

        try:
            add_files(request.remote_addr, req["listen_port"], req["files"])
            return {"success": True}, 201
        except IsNotAliveError as e:
            return {"error": str(e)}, 401
        except InvalidRequestError as e:
            return {"error": str(e)}, 400

    @app.route("/search", methods=["POST"])
    def search_files():
        req = request.get_json(force=True)

        try:
            return get_files(request.remote_addr, req["listen_port"])
        except IsNotAliveError as e:
            return {"error": str(e)}, 401
        except InvalidRequestError as e:
            return {"error": str(e)}, 400

    @app.route("/iamalive", methods=["POST"])
    def alive():
        req = request.get_json(force=True)

        try:
            refresh_peer(request.remote_addr, req["listen_port"])
            return {"alive": True}
        except IsNotAliveError as e:
            return {"error": str(e)}, 401
        except InvalidRequestError as e:
            return {"error": str(e)}, 400

    return app