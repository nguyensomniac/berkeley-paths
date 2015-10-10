import datetime
from app import db

class User(db.Document):
  user_id = db.IntField(required=True)
  last_updated = db.DateTimeField(default=datetime.datetime.now, required=True)
  days = db.ListField(required=True)