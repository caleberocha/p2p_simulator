from threading import Thread
from time import sleep
import requests
from requests.api import request
from . import constants


class KeepAlive(Thread):
    def __init__(self, server_url, listen_port):
        super().__init__()
        self.running = True
        self.listen_port = listen_port
        self.server_url = server_url
        self.registered = True

    def run(self):
        while self.running:
            sleep(constants.ALIVE_TIME)
            try:
                rs = requests.post(
                    self.server_url + constants.REQ_IAMALIVE, json={"listen_port": self.listen_port}
                )
                if rs.status_code == 200:
                    self.registered = True
                if rs.status_code == 401:
                    self.registered = False
                    print(f"""\r{rs.json()["error"]}\n""", end="")
                    self.stop()
            except requests.exceptions.ConnectionError:
                print("""\rERROR: Server offline\n""", end="")
                self.stop()

    def stop(self):
        self.running = False