import os
from threading import Thread
import socket
from . import constants


class Listener(Thread):
    def __init__(self, port=constants.LISTEN_PORT):
        super().__init__()
        self.files = []
        self.socket = None
        self.listening = True
        self.port = port

    def register_files(self, files):
        self.files = files

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.settimeout(1)

        self.socket.listen(5)

        while self.listening:
            conn = None
            try:
                conn, addr = self.socket.accept()
            except socket.timeout:
                continue

            try:
                data = conn.recv(1024)
                filehash = data.decode("utf-8")
                print(f"\rfilehash: {filehash}\n>", end="")
                self.send_file(filehash, conn, addr)
            finally:
                conn.close()

    def stop(self):
        self.listening = False

    def send_file(self, filehash, conn, addr):
        filename = next((f["name"] for f in self.files if f["hash"] == filehash), None)
        print(f"\rServer: Sending file {filename} to {addr}\n>", end="")
        if filename is None:
            conn.sendall(constants.FILE_NOT_FOUND)
        else:
            with open(os.path.join(constants.DIRECTORY_TO_SHARE, filename), "rb") as f:
                conn.sendall(f.read())