from .db import db
from .models.peer import Peer
from .models.file import File

def create_tables():
    db.create_tables([Peer, File])