import sys
from .peer import Peer
from . import constants

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        port = constants.LISTEN_PORT

    peer = Peer("http://127.0.0.1:5000", port)
    peer.start()