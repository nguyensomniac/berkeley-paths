from flask import Flask
from flask.ext.mongoengine import MongoEngine
import os, logging, sys
app = Flask(__name__, instance_relative_config=True)
if os.environ.get("ENV") != "heroku":
  app.config.from_pyfile('config.py')
else:
  app.config.from_object(os.environ)
  print(app.config)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
db = MongoEngine(app)
from app import routes