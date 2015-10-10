from flask import Flask, render_template, request, Response
from app import app
from .models import User
import requests, datetime, json
from .keys import keys

#constants
CAMPUS_MAP = "campus.shp"

## Open shapefile


## Make a request to the Moves API
def moves(url, params):
  base = "https://api.moves-app.com/api/1.1"
  return requests.get(base + url, params=params)

@app.route("/")
def display():
  return render_template('index.html')

@app.route("/auth")
def get_auth_token():
  code = request.args.get("code")
  params = {
    "grant_type": "authorization_code",
    "code": code,
    "client_id": keys["moves"]["public"],
    "client_secret": keys["moves"]["private"]
  }
  auth_token_request = requests.post("https://api.moves-app.com/oauth/v1/access_token", params=params)
  access_token = auth_token_request.json()["access_token"]
  summary = moves("/user/places/daily", {"pastDays": 31, "access_token": access_token})
  if summary.status_code == requests.codes.ok:
    user_id = auth_token_request.json()["user_id"]
    if User.objects(user_id = user_id):
      allDays = User.objects(user_id = user_id)[0]["days"]
      # for 
      #User.objects(user_id = user_id).update_one(days = summary.json(), last_updated = datetime.datetime.now).save()
    else:
      new_user = User(user_id = user_id, days = summary.json(), last_updated = datetime.datetime.now).save()
    return "Success!"
  return "Something wrong happened"
  # return render_template("moves.html", data=summary.json())

@app.route("/paths_data")
def get_paths_data():
  data = User.objects.all().to_json()
  return Response(json.dumps(data), mimetype='application/json')

@app.route("/map")
def render_map():
  return render_template("map.html")