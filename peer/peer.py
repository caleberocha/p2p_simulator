import os
from os.path import isfile
import hashlib
import requests
from requests.models import HTTPError
from tabulate import tabulate
from humanize import naturalsize
from .listener import Listener
from .keep_alive import KeepAlive
from .download import download_file, list_downloaded_files
from . import constants


class Peer:
    def __init__(self, server, listen_port):
        self.server = server
        self.listen_port = listen_port
        self.registered = False
        self.files = []
        self.listener = Listener(self.listen_port)
        self.keep_alive_thread = None

    def register(self):
        rs = requests.post(
            self.server + constants.REQ_REGISTER,
            json={"listen_port": self.listen_port},
        )
        if 400 <= rs.status_code < 600:
            raise HTTPError(f"""HTTP {rs.status_code} - {rs.json()["error"]}""")

        self.registered = True

    def keep_alive(self):
        self.keep_alive_thread = KeepAlive(self.server, self.listen_port)
        self.keep_alive_thread.start()

    def offerfiles(self):
        folder = os.path.expandvars(constants.DIRECTORY_TO_SHARE)
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if isfile(filepath):
                with open(filepath, "rb") as f:
                    self.files.append(
                        {
                            "name": filename,
                            "size": os.path.getsize(filepath),
                            "hash": hashlib.sha256(f.read()).hexdigest(),
                        }
                    )

        rs = requests.post(
            self.server + constants.REQ_OFFERFILES,
            json={"listen_port": self.listen_port, "files": self.files},
        )
        if 400 <= rs.status_code < 600:
            raise HTTPError(f"""HTTP {rs.status_code} - {rs.json()["error"]}""")

    def search(self):
        print("Searching files")

        rs = requests.post(
            self.server + constants.REQ_SEARCH, json={"listen_port": self.listen_port}
        )
        if 400 <= rs.status_code < 600:
            raise HTTPError(f"""HTTP {rs.status_code} - {rs.json()["error"]}""")

        files = rs.json()["files"]
        if len(files) == 0:
            print("No files found")
            return

        print(f"""{len(files)} file{"s" if len(files) > 1 else ""} found:""")
        print(
            tabulate(
                [
                    (
                        i,
                        f["name"],
                        naturalsize(f["size"], binary=True),
                        f["hash"],
                        len(f["peers"]),
                    )
                    for i, f in enumerate(files)
                ],
                headers=["#", "Name", "Size", "Hash", "Peers"],
            )
        )

        while True:
            idx = input(
                "Which file do you want to download? (Use # number or press c to cancel) "
            )
            if idx == "c":
                return
            try:
                i = int(idx)
                fr = files[i]
                download_file(fr["name"], fr["hash"], fr["size"], fr["peers"])
                return
            except (ValueError, IndexError):
                print("Invalid value")

    def start(self):
        try:
            print("Registering")
            self.register()

            print("Offering files... ", end="")
            self.offerfiles()
            print(f"{len(self.files)} files offered")

            print("Keeping alive")
            self.keep_alive()

            print("Creating listener")
            self.listener.register_files(self.files)
            self.listener.start()
            print()
        except requests.exceptions.ConnectionError:
            print("ERROR: Server offline")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

        self.help()
        while True:
            if not self.keep_alive_thread.registered:
                break

            cmd = input("> ").lower()
            if cmd in ["q", "quit"]:
                break

            if cmd in ["h", "help"]:
                self.help()
            elif cmd in ["l", "list"]:
                list_downloaded_files()
            elif cmd in ["s", "search"]:
                try:
                    self.search()
                except requests.exceptions.ConnectionError:
                    print("ERROR: Server offline")
                    break
                except HTTPError as e:
                    print(e)
                    break
            else:
                print("Invalid command")

        self.stop()

    def stop(self):
        self.listener.stop()
        self.keep_alive_thread.stop()
        print("Exiting")

    def help(self):
        print(
            "\n".join(
                [
                    "Commands:",
                    "s -> Search",
                    "q -> Qquit",
                    "l -> List downloaded files",
                    "h -> Show commands",
                ]
            )
        )
