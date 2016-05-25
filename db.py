import os
from datetime import datetime
from peewee import *
from playhouse.db_url import connect
from playhouse.postgres_ext import *
# from playhouse.migrate import *

db_url = os.environ.get('DATABASE_URL') or 'postgres://postgres:mysecretpassword@localhost:5432/marvel'
split = db_url.split(':')
split = ['postgresext' if i is 0 else e for i, e in enumerate(split)]
db_url = ':'.join(split)

db = connect(db_url)
# migrator = PostgresqlMigrator(db)

class Comic(Model):
    id = PrimaryKeyField()
    title = CharField()
    start = IntegerField()
    end = IntegerField(null=True)
    scraped = BooleanField(default=False)
    refreshed_at = DateTimeField(null=True)
    search_title = TSVectorField()

    class Meta:
        database = db


class Issue(Model):
    id = PrimaryKeyField()
    title = CharField()
    link = CharField()
    num = FloatField(null=True)
    series = ForeignKeyField(Comic)

    class Meta:
        database = db


# refreshed_at = DateTimeField(null=True)
# migrate(
#     migrator.drop_column('comic', 'refreshed_at'),
#     migrator.add_column('comic', 'refreshed_at', refreshed_at),
# )
