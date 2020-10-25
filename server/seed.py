from .db import db

# from .models.peer import Peer
# from .models.file import File
from .models import Peer, File, FilePeer


def create_tables():
    db.create_tables([Peer, File, FilePeer])