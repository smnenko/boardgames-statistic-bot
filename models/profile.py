from datetime import datetime

import inject
import peewee

from models.board import Board
from models.user import User


db = inject.instance(peewee.PostgresqlDatabase)


class Profile(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    board = peewee.ForeignKeyField(Board, backref='profiles')
    user = peewee.ForeignKeyField(User, backref='profiles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
