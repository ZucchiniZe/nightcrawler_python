from peewee import *
from playhouse.sqlite_ext import *

db = SqliteExtDatabase('marvel.db', threadlocals=True)

class Comic(Model):
    id = PrimaryKeyField()
    title = CharField()
    start = IntegerField()
    end = IntegerField(null=True)
    scraped = BooleanField(default=False)

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

class ComicSearch(FTSModel):
    comic_id = IntegerField()
    title = TextField()

    class Meta:
        database = db
