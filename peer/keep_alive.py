from threading import Thread
from time import sleep
import requests
from . import constants


class KeepAlive(Thread):
    def __init__(self, server_url, client_addr):
        super().__init__()
        self.running = True
        self.server_url = server_url
        self.client_addr = client_addr
        self.registered = True

    def run(self):
        while self.running:
            sleep(constants.ALIVE_TIME)
            rs = requests.post(
                self.server_url + constants.REQ_IAMALIVE, json={"ip": self.client_addr}
            )
            if rs.status_code == 200:
                self.registered = True
            if rs.status_code == 401:
                self.registered = False
                print(f"""\r{rs.json()["error"]}\n""", end="")
                self.stop()

    def stop(self):
        self.running = False