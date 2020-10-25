from peewee import *
from .db import db


class BaseModel(Model):
    class Meta:
        database = db


class File(BaseModel):
    name = CharField(unique=True)
    filehash = CharField(max_length=64, unique=True)


class Peer(BaseModel):
    ip = CharField(unique=True)
    last_login = DateTimeField(null=True)
    files = ManyToManyField(File, backref="peers")


FilePeer = Peer.files.get_through_model()
