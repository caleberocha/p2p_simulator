import os
from datetime import datetime, timedelta
from peewee import DoesNotExist, fn
from . import constants
from .models import File, Peer, FilePeer
from .errors import InvalidRequestError, IsNotAliveError


def max_alive_time():
    return datetime.now() - timedelta(
        seconds=int(os.getenv("ALIVE_TIME"))
        if os.getenv("ALIVE_TIME")
        else constants.ALIVE_TIME
    )


def get_alive_peer(addr):
    try:
        return (
            Peer.select()
            .where(
                Peer.address == addr,
                Peer.last_login >= max_alive_time(),
            )
            .get()
        )
    except DoesNotExist:
        raise IsNotAliveError("You are not registered")


def register_peer(host, port):
    try:
        addr = f"{host}:{int(port)}"
    except ValueError:
        raise InvalidRequestError("invalid listen_port")

    try:
        peer = Peer.get(address=addr)
        peer.last_login = datetime.now()
        peer.save()
    except DoesNotExist:
        peer = Peer.create(address=addr, last_login=datetime.now())


def refresh_peer(host, port):
    try:
        addr = f"{host}:{int(port)}"
    except ValueError:
        raise InvalidRequestError("invalid listen_port")

    peer = get_alive_peer(addr)

    peer.last_login = datetime.now()
    peer.save()


def add_files(host, port, files):
    try:
        addr = f"{host}:{int(port)}"
    except ValueError:
        raise InvalidRequestError("invalid listen_port")

    peer = get_alive_peer(addr)

    peer.files.clear()
    for f in files:
        # print(f"Adding {f}")
        try:
            filerow = File.get(filehash=f["hash"])
        except DoesNotExist:
            filerow = File.create(name=f["name"], size=f["size"], filehash=f["hash"])

        filerow.peers.add(peer)


def get_files(host, port):
    try:
        addr = f"{host}:{int(port)}"
    except ValueError:
        raise InvalidRequestError("invalid listen_port")

    peer = get_alive_peer(addr)

    files = (
        File.select(
            File.name,
            File.size,
            File.filehash.alias("hash"),
            fn.GROUP_CONCAT(Peer.address).alias("peers"),
        )
        .join(FilePeer)
        .join(Peer)
        .where(Peer.address != addr, Peer.last_login >= max_alive_time())
        .group_by(File)
        .dicts()
    )
    return {
        "files": [
            {"name": f["name"], "size": f["size"], "hash": f["hash"], "peers": f["peers"].split(",")}
            for f in files
        ]
    }
