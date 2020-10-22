from datetime import datetime
from flask import Flask, request
from .classes.peer import Peer, DoesNotExist
from .classes.file import File


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
            peer = Peer.select().where(Peer.ip == req["ip"]).get()
        except DoesNotExist:
            return {"error": "You are not registered"}, 401

        files = req["files"]

        File.delete().where(File.peer == peer).execute()
        for f in files:
            File.create(name=f["name"], filehash=f["hash"], peer=peer)

        return {"success": True}, 201

    @app.route("/search", methods=["GET"])
    def search_files():
        files = File.select(File.name, File.filehash.alias("hash"), Peer.ip).join(Peer).dicts()
        return {"files": [f for f in files]}

    return app