from datetime import datetime

import peewee

import main
from constants import GameScoreChoice


__all__ = ('User', 'Board', 'Profile', 'Game', 'GameRole', 'GameResult')


class User(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    chat_id = peewee.IntegerField(unique=True)
    username = peewee.CharField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db


class Board(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    group_id = peewee.IntegerField(null=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db


class Profile(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    board = peewee.ForeignKeyField(Board, backref='profiles')
    user = peewee.ForeignKeyField(User, backref='profiles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db


class Game(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField()
    slug = peewee.CharField()

    is_visible = peewee.BooleanField(default=False)
    is_active = peewee.BooleanField(default=True)
    is_score = peewee.BooleanField(default=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db


class GameRole(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField()
    parent = peewee.ForeignKeyField('self', null=True, backref='parent')

    game = peewee.ForeignKeyField(Game, backref='roles')

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db


class GameResult(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    profile = peewee.ForeignKeyField(Profile, backref='results')
    game = peewee.ForeignKeyField(Game, backref='results')

    role = peewee.ForeignKeyField(GameRole, backref='results', null=True)
    score = peewee.IntegerField(choices=GameScoreChoice, null=True)
    is_win = peewee.BooleanField(null=True)

    is_filled = peewee.BooleanField(default=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = main.db
