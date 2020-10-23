import os
from datetime import datetime, timedelta
from server.errors import IsNotAliveError
from flask import Flask, request
from .models.peer import Peer, DoesNotExist
from .models.file import File
from . import constants


def create_app():
    app = Flask(__name__)

    @app.route("/register", methods=["POST"])
    def register():
        req = request.get_json(force=True)

        Peer.replace(ip=req["ip"], last_login=datetime.now()).execute()
        return {"success": True}

    @app.route("/offerfiles", methods=["POST"])
    def offer_files():
        req = request.get_json(force=True)

        try:
            peer = get_alive_peer(req["ip"])
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

        files = req["files"]

        File.delete().where(File.peer == peer).execute()
        for f in files:
            File.create(name=f["name"], filehash=f["hash"], peer=peer)

        return {"success": True}, 201

    @app.route("/search", methods=["POST"])
    def search_files():
        req = request.get_json(force=True)

        try:
            peer = get_alive_peer(req["ip"])
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

        files = (
            File.select(File.name, File.filehash.alias("hash"), Peer.ip)
            .join(Peer)
            .dicts()
        )
        return {"files": [f for f in files]}

    @app.route("/iamalive", methods=["POST"])
    def alive():
        req = request.get_json(force=True)

        try:
            peer = get_alive_peer(req["ip"])
        except IsNotAliveError as e:
            return {"error": str(e)}, 401

        peer.last_login = datetime.now()
        peer.save()

        return {"alive": True}

    def get_alive_peer(ip):
        try:
            return (
                Peer.select()
                .where(
                    Peer.ip == ip,
                    Peer.last_login
                    >= datetime.now()
                    - timedelta(
                        seconds=int(os.getenv("ALIVE_TIME"))
                        if os.getenv("ALIVE_TIME")
                        else constants.ALIVE_TIME
                    ),
                )
                .get()
            )
        except DoesNotExist:
            raise IsNotAliveError("You are not registered")

    return app