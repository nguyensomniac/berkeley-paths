from flask import Flask
from flask.ext.mongoengine import MongoEngine
import os, logging, sys
app = Flask(__name__, instance_relative_config=True)
if os.environ.get("ENV") != "heroku":
  app.config.from_pyfile('config.py')
else:
  # Heroku environment variables are in os.environ, which can be converted into a dict.
  # Iterate through this dict to create app config.
  heroku_config = os.environ.copy()
  for k in heroku_config:
    if k.isupper():
      app.config[k] = heroku_config[k]
  print(app.config)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
db = MongoEngine(app)
from app import routes