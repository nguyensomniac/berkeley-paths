from flask import Flask, session, render_template, request, Response, redirect, url_for, make_response, abort
from app import app
from app import map as m
from app import moves
from .models import User
import requests, datetime, json

# Store access tokens associated with a User ID. If user with that ID does not exist, create said user.
# Returns boolean corresponding to whether save was successful.
def store_access_tokens(user_id, access_token, refresh_token):
  try:
    User.objects(user_id = user_id).update_one(
      access_token = access_token, 
      refresh_token = refresh_token,
      last_updated = datetime.datetime.now(), upsert=True).save()
    return True
  except Exception:
    return False

def store_map_data(data):
  try:
    u = User.objects.get(user_id = session["user_id"])
    u.days = data
    u.last_updated = datetime.datetime.now()
    u.save()
    return True
  except Exception as e:
    print(e)
    return False

def store_survey_data(year, major):
  try:
    u = User.objects.get(user_id = session["user_id"])
    u.year = year
    u.major = major
    u.last_updated = datetime.datetime.now()
    u.save()
    return True
  except Exception as e:
    print(e)
    return False

@app.route("/")
def display():
  return render_template('index.html', moves_key=app.config["MOVES_PUBLIC"])

# Get auth token and set session variable
@app.route("/auth")
def get_auth_token():
  code = request.args.get("code")
  params = {
    "grant_type": "authorization_code",
    "code": code,
    "client_id": app.config["MOVES_PUBLIC"],
    "client_secret": app.config["MOVES_PRIVATE"]
  }
  auth_token_request = moves.moves_auth("access_token", params)
  try:
    user_id = auth_token_request.json()["user_id"]
    access_token = auth_token_request.json()["access_token"]
    refresh_token = auth_token_request.json()["refresh_token"]
    store_access_tokens(user_id, access_token, refresh_token)
    session["moves_access_token"] = access_token
    session["user_id"] = auth_token_request.json()["user_id"]
    return redirect(url_for('display_survey'))
  except KeyError:
    return "Something wrong happened"

# Get storyline data and filter it. Return JSON of the current user's location data.
@app.route("/storyline")
def dump_storyline():
  return Response(json.dumps(m.update_storyline(session["user_id"])))

@app.route("/survey")
def display_survey():
  map_data = m.update_storyline(session["user_id"])
  if(map_data.get("error", None) == None):
    store_map_data(map_data)
  return render_template("survey.html")

@app.route("/paths_all")
def get_paths_data():
  data = User.objects.all().to_json()
  return Response(json.dumps(data), mimetype='application/json')

@app.route("/paths_current")
def current_user_paths():
  try:
    u = User.objects.get(user_id = session["user_id"]).to_json()
    return Response(json.dumps(u))
  except DoesNotExist:
    return abort(500)

@app.route("/map")
def render_map():
  return render_template("map.html")

@app.route("/survey_submit", methods=["POST"])
def survey_submit():
  year = int(request.form["year"])
  major = request.form["major"]
  if store_survey_data(year, major):
    return render_template("submitted.html")
  else:
    return abort(500)

@app.errorhandler(404)
def not_found(err):
  return render_template("404.html")

@app.errorhandler(500)
def not_found(err):
  return render_template("500.html")