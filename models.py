from peewee import *


class User(Model):
    user_id = IntegerField(unique=True, primary_key=True)
    crypts = TextField()
    actions = TextField()

    class Meta:
        database = SqliteDatabase('db.db')
