from datetime import datetime

import inject
import peewee


db = inject.instance(peewee.PostgresqlDatabase)


class User(peewee.Model):
    id = peewee.BigAutoField(primary_key=True, unique=True)

    chat_id = peewee.BigIntegerField(unique=True)
    username = peewee.CharField(null=True)

    created_at = peewee.DateTimeField(default=datetime.now())
    updated_at = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
