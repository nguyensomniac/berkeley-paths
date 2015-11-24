# Contains all functions relating to the Moves API.

import requests, datetime

# Make a request to the Moves API
def moves(url, params):
  base = "https://api.moves-app.com/api/1.1"
  return requests.get(base + url, params=params)

# Make a request to the OAuth endpoints of the Moves API.
def moves_auth(url, params):
  base = "https://api.moves-app.com/oauth/v1/"
  return requests.post(base + url, params=params)

# Parse lastUpdate string from Moves.
def format_lastupdate(d):
  format = "%Y%m%dT%H%M%SZ"
  return datetime.datetime.strptime(d, format)

#Get day of the week (in English) from a date string from the Moves API
def get_weekday(str):
  day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "monday"]
  format = "%Y%m%d"
  d = datetime.datetime.strptime(str, format)
  return day_names[d.weekday()]