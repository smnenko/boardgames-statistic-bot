from datetime import datetime

import inject
import peewee

from constants import ProfileResultStatusChoice
from models.game_result import GameResult
from models.game_role import GameRole
from models.profile import Profile


db = inject.instance(peewee.PostgresqlDatabase)


class ProfileResult(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    game_result = peewee.ForeignKeyField(GameResult, backref='profile_results', on_delete='CASCADE')
    profile = peewee.ForeignKeyField(Profile, backref='results', on_delete='CASCADE')
    role = peewee.ForeignKeyField(GameRole, backref='results', null=True, on_delete='CASCADE')
    status = peewee.IntegerField(choices=ProfileResultStatusChoice, null=True)
    score = peewee.IntegerField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
