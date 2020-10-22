import os
from peewee import SqliteDatabase
from . import constants

db = SqliteDatabase(os.getenv("APPDB") if os.getenv("APPDB") else constants.DBFILE)

