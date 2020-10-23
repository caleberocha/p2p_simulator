from peewee import *
from .base_model import BaseModel


class Peer(BaseModel):
    ip = CharField(unique=True)
    last_login = DateTimeField(null=True)