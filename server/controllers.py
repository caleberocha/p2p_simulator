import os
from datetime import datetime, timedelta
from peewee import DoesNotExist, fn
from . import constants
from .models import File, Peer, FilePeer
from .errors import IsNotAliveError


def max_alive_time():
    return datetime.now() - timedelta(
        seconds=int(os.getenv("ALIVE_TIME"))
        if os.getenv("ALIVE_TIME")
        else constants.ALIVE_TIME
    )


def get_alive_peer(ip):
    try:
        return (
            Peer.select()
            .where(
                Peer.ip == ip,
                Peer.last_login >= max_alive_time(),
            )
            .get()
        )
    except DoesNotExist:
        raise IsNotAliveError("You are not registered")


def register_peer(ip):
    try:
        peer = Peer.get(ip=ip)
        peer.last_login = datetime.now()
        peer.save()
    except DoesNotExist:
        peer = Peer.create(ip=ip, last_login=datetime.now())


def refresh_peer(ip):
    peer = get_alive_peer(ip)

    peer.last_login = datetime.now()
    peer.save()


def add_files(ip, files):
    peer = get_alive_peer(ip)

    peer.files.clear()
    for f in files:
        try:
            filerow = File.get(filehash=f["hash"])
        except DoesNotExist:
            filerow = File.create(name=f["name"], size=f["size"], filehash=f["hash"])

        filerow.peers.add(peer)


def get_files(ip):
    peer = get_alive_peer(ip)

    files = (
        File.select(
            File.name,
            File.filehash.alias("hash"),
            fn.GROUP_CONCAT(Peer.ip).alias("peers"),
        )
        .join(FilePeer)
        .join(Peer)
        .where(Peer.ip != ip, Peer.last_login >= max_alive_time())
        .group_by(File)
        .dicts()
    )
    return {
        "files": [
            {"name": f["name"], "hash": f["hash"], "peers": f["peers"].split(",")}
            for f in files
        ]
    }
