import os
import sys
from .peer import Peer
from . import constants

if __name__ == "__main__":
    try:
        listen_port = int(sys.argv[1])
    except (ValueError, IndexError):
        listen_port = constants.LISTEN_PORT

    try:
        server = sys.argv[2]
    except IndexError:
        server = constants.SERVER_URL

    peer = Peer(server, listen_port)
    peer.start()