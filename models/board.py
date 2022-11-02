from datetime import datetime

import inject
import peewee


db = inject.instance(peewee.PostgresqlDatabase)


class Board(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)
    group_id = peewee.BigIntegerField(null=False)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
