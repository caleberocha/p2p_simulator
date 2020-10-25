from .peer import Peer

if __name__ == "__main__":
    peer = Peer("http://127.0.0.1:5000")
    peer.start()