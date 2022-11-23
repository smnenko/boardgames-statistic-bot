from datetime import datetime

import inject
import peewee

from constants import GameResultStatus
from models.board import Board
from models.game import Game


db = inject.instance(peewee.PostgresqlDatabase)


class GameResult(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    board = peewee.ForeignKeyField(Board, backref='results')
    game = peewee.ForeignKeyField(Game, backref='results')
    status = peewee.IntegerField(choices=GameResultStatus, default=GameResultStatus.STARTED.value)

    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
