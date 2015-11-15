from flask import Flask
from flask.ext.mongoengine import MongoEngine
import os
app = Flask(__name__, instance_relative_config=True)
print(os.environ)
if os.environ.get("ENV") is not "heroku":
  app.config.from_pyfile('config.py')
else:
  app.config.from_object(os.environ)
db = MongoEngine(app)
from app import routes