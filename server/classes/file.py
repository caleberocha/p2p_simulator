from peewee import *
from .base_model import BaseModel
from .peer import Peer


class File(BaseModel):
    name = CharField(unique=True)
    filehash = CharField(max_length=64, unique=True)
    peer = ForeignKeyField(Peer, backref="files")
