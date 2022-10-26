from datetime import datetime

import inject
import peewee

from constants import ProfileResultStatusChoice, GameResultStatus


__all__ = ('User', 'Board', 'Profile', 'Game', 'GameRole', 'ProfileResult', 'GameResult')


db = inject.instance(peewee.PostgresqlDatabase)


class User(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    chat_id = peewee.BigIntegerField(unique=True)
    username = peewee.CharField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class Board(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    group_id = peewee.BigIntegerField(null=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class Profile(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    board = peewee.ForeignKeyField(Board, backref='profiles')
    user = peewee.ForeignKeyField(User, backref='profiles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class Game(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField(null=True)

    board = peewee.ForeignKeyField(Board, backref='games', null=True)

    is_visible = peewee.BooleanField(default=False)
    is_active = peewee.BooleanField(default=True)
    is_score = peewee.BooleanField(default=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class GameRole(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField()
    parent = peewee.ForeignKeyField('self', null=True, backref='parent')

    game = peewee.ForeignKeyField(Game, backref='roles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class GameResult(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    board = peewee.ForeignKeyField(Board, backref='results')
    game = peewee.ForeignKeyField(Game, backref='results')
    status = peewee.IntegerField(choices=GameResultStatus, default=GameResultStatus.STARTED.value)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db


class ProfileResult(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    game_result = peewee.ForeignKeyField(GameResult, backref='profile_results', on_delete='CASCADE')
    profile = peewee.ForeignKeyField(Profile, backref='results', on_delete='CASCADE')
    role = peewee.ForeignKeyField(GameRole, backref='results', null=True, on_delete='CASCADE')
    status = peewee.IntegerField(choices=ProfileResultStatusChoice, null=True)
    score = peewee.IntegerField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
