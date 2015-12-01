from app import map as m
from app import moves
from app.models import User
import time, requests, datetime, os

MAX_TRIES = 3

def update_map_data():
  users = User.objects(access_token__exists=True)
  for user in users:
    new_data = m.update_storyline(user.user_id)
    tries = 0
    while new_data.get("error", None) != None and tries < MAX_TRIES:
      print(new_data.get("error"))
      if new_data["error"] == "Rate limited":
        time.sleep(60)
        new_data = m.update_storyline(user.user_id)
      elif new_data["error"] == "Invalid access token":
        params = {
          "grant_type": "refresh_token",
          "refresh_token": user.refresh_token,
          "client_id": app.config["MOVES_PUBLIC"],
          "client_secret": app.config["MOVES_PRIVATE"]
        }
        new_token = moves.moves_auth("access_token", params)
        if new_token.status_code == requests.codes.ok:
          user.access_token = new_token.json()["access_token"]
          user.refresh_token = new_token.json()["refresh_token"]
          new_data = m.update_storyline(user.user_id)
      tries+= 1
    if new_data.get("error", None) != None:
      if new_data["error"] == "Invalid access token":
        user.update(unset__access_token).update(unset__refresh_token)
    elif new_data != user.days and new_data != None:
      user.days = new_data
    user.last_updated = datetime.datetime.now()
    user.save()
update_map_data()