import os
import socket
from datetime import datetime, timezone
from tabulate import tabulate
from . import constants


def download_file(filename, filehash, filesize, peers):
    addr = peers[0].split(":")
    addr[1] = int(addr[1])
    addr = tuple(addr)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)

    try:
        sock.sendall(bytes(filehash, "utf-8"))

        if not os.path.exists(constants.DOWNLOAD_DIRECTORY):
            os.makedirs(constants.DOWNLOAD_DIRECTORY)

        with open(os.path.join(constants.DOWNLOAD_DIRECTORY, filename), "wb") as f:
            print(f"Downloading {filename}... ", end="")
            bytes_downloaded = 0
            while True:
                data = sock.recv(1024)
                if data is None or len(data) == 0:
                    break
                f.write(data)
                bytes_downloaded += len(data)
                print(
                    f"\rDownloading {filename}... {bytes_downloaded} of {filesize} bytes",
                    end="",
                )
            f.close()
            print(f"\nDownload complete")
    finally:
        sock.close()


def list_downloaded_files():
    files = []
    try:
        for f in os.listdir(constants.DOWNLOAD_DIRECTORY):
            fp = os.path.join(constants.DOWNLOAD_DIRECTORY, f)
            stat = os.stat(fp)
            files.append(
                {
                    "Name": f,
                    "Size": stat.st_size,
                    "Date": datetime.fromtimestamp(stat.st_mtime).astimezone(),
                }
            )
    except FileNotFoundError:
        print("No files downloaded")

    print(tabulate(files, headers="keys"))