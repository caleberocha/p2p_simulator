from .db import db
from .classes.peer import Peer
from .classes.file import File

def create_tables():
    db.create_tables([Peer, File])