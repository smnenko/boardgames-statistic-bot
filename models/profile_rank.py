from datetime import datetime

import inject
import peewee

from models import Profile


db = inject.instance(peewee.PostgresqlDatabase)


class Rank(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    name = peewee.CharField()
    points = peewee.IntegerField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db

    @classmethod
    def get_by_points(cls, points: int):
        return cls.select().where(Rank.points <= points).get()


class ProfileRank(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    profile = peewee.ForeignKeyField(Profile, backref='rank', unique=True)
    points = peewee.IntegerField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
