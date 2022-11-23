from datetime import datetime

import inject
import peewee

from models.board import Board


db = inject.instance(peewee.PostgresqlDatabase)


class Game(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField(null=True)

    board = peewee.ForeignKeyField(Board, backref='games', null=True)

    is_visible = peewee.BooleanField(default=False)
    is_active = peewee.BooleanField(default=True)
    is_score = peewee.BooleanField(default=False)

    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
