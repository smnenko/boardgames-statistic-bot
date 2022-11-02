from datetime import datetime

import inject
import peewee

from models.game import Game


db = inject.instance(peewee.PostgresqlDatabase)


class GameRole(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField()
    parent = peewee.ForeignKeyField('self', null=True, backref='children')

    game = peewee.ForeignKeyField(Game, backref='roles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
