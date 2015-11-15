from flask import Flask, session, render_template, request, Response, redirect, url_for, make_response
from app import app
from .models import User
from mongoengine.queryset import DoesNotExist
import requests, datetime, json, fiona
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep

# constants
CAMPUS_MAP = "./app/data/campus.shp"

# Open shapefile m and prepare polygons for comparison
def prepare_map(m):
  shape = fiona.open(m)
  geom = [record["geometry"] for record in list(shape)]
  shape.close()
  polygons = [Polygon(g["coordinates"][0]) for g in geom]
  return prep(MultiPolygon(polygons))

# Returns true if point is in m
def latLonContains(m, p):
  pt = Point(p["lon"], p["lat"])
  return m.contains(pt)

# Inputs an item in the list of daily summaries generated from the Moves API.
# That item is a dict with an array of segments, which are either of type "move"
# or type "place".
# Outputs that same item, but for each segment, filter out all the places that aren't
# in the map and activities without track points within the map.
def points_contained(map, day):
  new_segments = []
  if day["segments"] != None:
    for seg in day["segments"]:
      if seg["type"] == "place":
        if latLonContains(map, seg["place"]["location"]):
          new_segments.append(seg)
      elif seg["activities"] != None:
        new_activities = []
        for a in seg["activities"]:
          a["trackPoints"] = [t for t in a["trackPoints"] if latLonContains(map, t)]
          if len(a["trackPoints"]):
            new_activities.append(a)
        if len(new_activities):
          seg["activities"] = new_activities
          new_segments.append(seg)
  day["segments"] = new_segments
  return day

# Parse date string from Moves (with timezone information if tz is true)
def format_date(d, tz = None):
  format = "%Y%m%dT%H%M%S"
  format = format + "%z" if tz else format + "Z"
  return datetime.datetime.strptime(d, format)

#Get day of the week (in English) from a date string from the Moves API
def get_weekday(str):
  day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "monday"]
  format = "%Y%m%d"
  d = datetime.datetime.strptime(str, format)
  return day_names[d.weekday()]

# Make a request to the Moves API
def moves(url, params):
  base = "https://api.moves-app.com/api/1.1"
  return requests.get(base + url, params=params)

#save user
def save_user(user_data):
  try:
    u = User.objects.get(user_id = session["user_id"])
    if user_data.get("summary", None) != None:
      u.days = user_data["summary"]
    if user_data.get("major", None) != None:
      u.major = user_data["major"]
    if user_data.get("year", None) != None:
      u.year = user_data["year"]
    u.last_updated = datetime.datetime.now
    u.save()
  except DoesNotExist:
    if user_data.get("summary", None) != None and session["user_id"] != None:
      new_user = User(user_id = session["user_id"], days = user_data["summary"], last_updated = datetime.datetime.now).save()
    else:
      return False
  return True

@app.route("/")
def display():
  return render_template('index.html')

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
  auth_token_request = requests.post("https://api.moves-app.com/oauth/v1/access_token", params=params)
  access_token = auth_token_request.json()["access_token"]
  if access_token != None:
    session["moves_access_token"] = access_token
    session["user_id"] = auth_token_request.json()["user_id"]
    return redirect(url_for('display_survey'))
  return "Something wrong happened"

# Get storyline data and filter it. Return JSON of the current user's location data.
@app.route("/storyline")
def get_storyline():
  m = prepare_map(CAMPUS_MAP)
  summary = moves("/user/storyline/daily", {
    "from": "20151005", "to": "20151011",
    # "pastDays": 7,
    "trackPoints": "true", "access_token": session["moves_access_token"]})
  if summary.status_code == requests.codes.ok:
    user_id = session["user_id"]
    new_days = {}
    s = summary.json()
    try:
      u = User.objects.get(user_id = user_id)
      new_days = u.days
      for day in s:
        weekday = get_weekday(day["date"])
        day_summary = points_contained(m, day)
        if len(day_summary["segments"]):
          try:
            if int(day["date"]) >= int(u.days[weekday]["date"]):
              new_days[weekday] = day_summary
          except KeyError:
            new_days[weekday] = day_summary
    except DoesNotExist:
      for day in s:
        weekday = get_weekday(day["date"])
        day_summary = points_contained(m, day)
        if len(day_summary):
          new_days[weekday] = day_summary
    return Response(json.dumps(new_days))
      # # Get index of first item in the API response that was updated after the user object's last update
      # first_new_index = 0
      # while first_new_index < len(s):
      #   moves_date = format_date(s[first_new_index]["lastUpdate"])
      #   if moves_date < u["last_updated"]:
      #     first_new_index += 1
      #   else:
      #     break
      # # if the index of the first new item == length of response, no new items
      # if first_new_index != len(s):
      #   if u.days[-1]["date"] == s[first_new_index]["date"]:
      #     old_days = u.days[:-1]
      #   else:
      #     old_days = u.days
      #   # filter points in new data that are not in map, and add them to the original array
      #   m = prepare_map(CAMPUS_MAP)
      #   new_days = points_contained(m, s[first_new_index:])
      #   old_days.extend(new_days)
      #   return Response(json.dumps(old_days), mimetype='application/json')
      # return Response(json.dumps(u.days), mimetype="application/json")

@app.route("/survey")
def display_survey():
  map_data = get_storyline()
  if map_data.status_code == requests.codes.ok:
    save_data = {
      "summary": json.loads(map_data.get_data().decode("utf-8"))
    }
    save_user(save_data)
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
    return make_response("Something wrong happened")

@app.route("/map")
def render_map():
  return render_template("map.html")

@app.route("/survey_submit", methods=["POST"])
def survey_submit():
  user_data = {
    "major": request.form["major"],
    "year": int(request.form["year"])
  }
  if save_user(user_data):
    return make_response("Success!")
  else:
    return make_response("Something wrong happened")
