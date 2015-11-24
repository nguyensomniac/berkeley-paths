import datetime
from app import db
from mongoengine.base import ValidationError

majors = [
  "ARTS",
  "BIOLOGY",
  "BUSINESS",
  "EECS",
  "ECON",
  "ENGINEER",
  "MATH",
  "NATURALRESOURCES",
  "POLITICAL",
  "SOCIAL",
  "OTHER"
]

class User(db.Document):
  user_id = db.IntField(required=True)
  year = db.IntField()
  major = db.StringField()
  last_updated = db.DateTimeField(default=datetime.datetime.now, required=True)
  days = db.DictField()
  access_token = db.StringField()
  refresh_token = db.StringField()
  def clean(self):
    # Raise validation error if major is not in list.
    if self.major != None and self.major not in majors:
      raise ValidationError("You submitted an invalid major.")
    if self.year != None and self.year > 5:
      raise ValidationError("You submitted an invalid year.")