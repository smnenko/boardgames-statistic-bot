# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class Board(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    group_id = BigIntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "board"


@snapshot.append
class Game(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    name = CharField(max_length=255, null=True)
    board = snapshot.ForeignKeyField(backref='games', index=True, model='board', null=True)
    is_visible = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_score = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "game"


@snapshot.append
class GameResult(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    board = snapshot.ForeignKeyField(backref='results', index=True, model='board')
    game = snapshot.ForeignKeyField(backref='results', index=True, model='game')
    status = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "gameresult"


@snapshot.append
class GameRole(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    name = CharField(max_length=255)
    parent = snapshot.ForeignKeyField(backref='children', index=True, model='@self', null=True)
    game = snapshot.ForeignKeyField(backref='roles', index=True, model='game')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "gamerole"


@snapshot.append
class User(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    chat_id = BigIntegerField(unique=True)
    username = CharField(max_length=255, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "user"


@snapshot.append
class Profile(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    board = snapshot.ForeignKeyField(backref='profiles', index=True, model='board')
    user = snapshot.ForeignKeyField(backref='profiles', index=True, model='user')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "profile"


@snapshot.append
class ProfileRank(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    profile = snapshot.ForeignKeyField(backref='rank', index=True, model='profile', unique=True)
    points = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "profilerank"


@snapshot.append
class ProfileResult(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    game_result = snapshot.ForeignKeyField(backref='profile_results', index=True, model='gameresult', on_delete='CASCADE')
    profile = snapshot.ForeignKeyField(backref='results', index=True, model='profile', on_delete='CASCADE')
    role = snapshot.ForeignKeyField(backref='results', index=True, model='gamerole', null=True, on_delete='CASCADE')
    status = IntegerField(null=True)
    score = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "profileresult"


@snapshot.append
class Rank(peewee.Model):
    id = BigAutoField(primary_key=True, unique=True)
    name = CharField(max_length=255)
    points = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = "rank"


