from hashlib import sha256
import os
from os.path import isfile
import sys
import socket
import json
import hashlib
import requests
from . import constants


class Peer:
    def __init__(self, server):
        self.server = server
        self.registered = False
        self.ip = socket.gethostbyname(socket.gethostname())
        self.files = []


    def register(self):
        rs = requests.post(self.server + constants.REQ_REGISTER, json={"ip": self.ip})
        rs.raise_for_status()
        self.registered = True

    def offerfiles(self):
        folder = os.path.expandvars(constants.DIRECTORY_TO_SHARE)
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if isfile(filepath):
                with open(filepath, "rb") as f:
                    self.files.append({"name": filename, "hash": hashlib.sha256(f.read()).hexdigest()})

        rs = requests.post(self.server + constants.REQ_OFFERFILES, json={"ip": self.ip, "files": self.files})
        rs.raise_for_status()

    def start(self):
        print("Registering")
        self.register()
        print("Offering files")
        self.offerfiles()
        print(f"{len(self.files)} files offered")
        

        

