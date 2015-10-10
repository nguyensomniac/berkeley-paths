from flask import Flask
from flask.ext.mongoengine import MongoEngine
app = Flask(__name__)
app.config['MONGODB_DB'] = 'berkeley-paths'
db = MongoEngine(app)
from app import routes