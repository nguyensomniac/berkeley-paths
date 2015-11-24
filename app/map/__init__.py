from flask import Flask, session
from app import app
import app.moves as moves
from ..models import User
import requests, datetime, json, fiona, os
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep

# constants
CAMPUS_MAP = os.path.join(os.path.dirname(__file__), "data/campus.shp")

# Open shapefile m with Shapely. This makes determining whether a point is
# in the bounds of the shapefile much faster.
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

# Moves API returns a summary for each day. Iterate through that 
# summary, mapping each date to its weekday. 
def update_storyline(user_id):
  u = User.objects.get(user_id = user_id)
  m = prepare_map(CAMPUS_MAP)
  summary = moves.moves("/user/storyline/daily", {
    "pastDays": 7,
    "trackPoints": "true", 
    "access_token": u.access_token
  })
  if summary.status_code == requests.codes.ok:
    new_days = {}
    s = summary.json()
    new_days = u.days
    for day in s:
      weekday = moves.get_weekday(day["date"])
      try:
        if (int(day["date"]) != int(u.days[weekday]["date"]) or
          moves.format_lastupdate(u.days[weekday]["lastUpdate"]) > moves.format_lastupdate(day["lastUpdate"])):
          continue
      except KeyError:
          pass
      finally:
        day_summary = points_contained(m, day)
        if len(day_summary["segments"]):
          new_days[weekday] = day_summary
    return new_days
  elif summary.status_code == 429:
    return {"error": "Rate limited"}
  elif summary.status_code == 401:
    return {"error": "Invalid access token"}
  return None