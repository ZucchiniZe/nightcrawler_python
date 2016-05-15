import os
from peewee import *
from playhouse.db_url import connect
from playhouse.postgres_ext import *

db = connect(os.environ.get('DATABASE') or 'postgresext://postgres:mysecretpassword@localhost:5432/marvel')

class Comic(Model):
    id = PrimaryKeyField()
    title = CharField()
    start = IntegerField()
    end = IntegerField(null=True)
    scraped = BooleanField(default=False)
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
