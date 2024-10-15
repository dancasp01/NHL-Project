# -------------- Imports and Setup ---------------
import requests
import pandas as pd
from pandas import json_normalize 
# from datetime import datetime
# from time import sleep
import random

team_abreviations = [
  # ------- Eastern Conference -------
  # --- Metro ---
  "CAR",  # Carolina Hurricanes
  "CBJ",  # Columbus Blue Jackets
  "NJD",  # New Jersey Devils
  "NYI",  # New York Islanders
  "NYR",  # New York Rangers
  "PHI",  # Philadelphia Flyers
  "PIT",  # Pittsburgh Penguins
  "WSH",   # Washington Capitals
  # --- Atlatic ---
  "BOS",  # Boston Bruins
  "BUF",  # Buffalo Sabres
  "DET",  # Detroit Red Wings
  "FLA",  # Florida Panthers
  "MTL",  # Montreal Canadiens
  "OTT",  # Ottawa Senators
  "TBL",  # Tampa Bay Lightning
  "TOR",   # Toronto Maple Leafs
  # ------- Western Conference -------
  # --- Central ---
  "ARI",  # Arizona Coyotes
  "CHI",  # Chicago Blackhawks
  "COL",  # Colorado Avalanche
  "DAL",  # Dallas Stars
  "MIN",  # Minnesota Wild
  "NSH",  # Nashville Predators
  "STL",  # St. Louis Blues
  "WPG",   # Winnipeg Jets
  # --- Pacific ---
  "ANA",  # Anaheim Ducks
  "CGY",  # Calgary Flames
  "EDM",  # Edmonton Oilers
  "LAK",  # Los Angeles Kings
  "SEA",  # Seattle Kraken
  "SJS",  # San Jose Sharks
  "VAN",  # Vancouver Canucks
  "VGK",  # Vegas Golden Knights
  "UTA"   # Utah Hockey Club
]

nhl_teams = [
  "Hockey Club"
  "Ducks",
  "Coyotes",
  "Bruins",
  "Sabres",
  "Flames",
  "Hurricanes",
  "Blackhawks",
  "Avalanche",
  "Blue Jackets",
  "Stars",
  "Red Wings",
  "Oilers",
  "Panthers",
  "Kings",
  "Wild",
  "Canadiens",
  "Predators",
  "Devils",
  "Islanders",
  "Rangers",
  "Senators",
  "Flyers",
  "Penguins",
  "Sharks",
  "Kraken",
  "Blues",
  "Lightning",
  "Maple Leafs",
  "Canucks",
  "Golden Knights",
  "Capitals",
  "Jets"
]

# -------------- Call to API ---------------

def call_nhl(url, start=None, end=None):

  # startSeason = 20232024
  # endSeason = 20232024

  # if start:
  #   startSeason = start

  # if end:
  #   endSeason = end
  
  # if endSeason < startSeason:
  #   return "End season cannot be befor start season"

  # # Possible to call API for multiple seasons, 
  # # but if no end season is provided, set end season = start season.
  # if not endSeason:
  #   endSeason = startSeason

  # Headers in the API call authenticate the requests
  headers = {
    'authority': 'api.nhle.com',
    # Could cycle through different user agents using the fake-useragent module 
    # if the API appears to be blocking repeated calls
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'accept': '*/*',
    'origin': 'http://www.nhl.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'http://www.nhl.com/',
    'accept-language': 'en-US,en;q=0.9',
  }

  params = (
    ('isAggregate', 'false'),
    ('isGame', 'true'),
    ('sort', '[{"property":"gameDate","direction":"DESC"}]'),
    ('start', '0'),
    # Setting limit = 0 returns all games for given season
    ('limit', '0'),
    ('factCayenneExp', 'gamesPlayed>=1'),
    # Through trial and error, gameTypeId=2 corresponds to regular season games
    # The f-string inserts endSeason and startSeason into the parameters
    # ('cayenneExp', f'gameTypeId=2 and seasonId<={endSeason} and seasonId>={startSeason}'),
  )
  
  # Call API with given headers and parameters
  response = requests.get(url, headers=headers, params=params)

  return response

# -------------- Data Methods ---------------

def get_all_playerIDs(season):
  
  if not season:
    season = 20232024

  forwards = []
  defensemen = []
  goalies = []

  for team in team_abreviations:

    try:
      response = call_nhl('https://api-web.nhle.com/v1/roster/'+ team + '/' + str(season))
      data = response.json()
    except Exception:
      print("Team: " + str(team) + " did not exist during that season")
      continue

    forwards_data = list(data['forwards'])
    defensemen_data = list(data['defensemen'])
    golies_data = list(data['goalies'])

    for forward_player in forwards_data:
      forwards.append(forward_player['id'])

    for defense_player in defensemen_data:
      defensemen.append(defense_player['id'])

    for goalie in golies_data:
      goalies.append(goalie['id'])

  return forwards + defensemen + goalies


def get_random_player(all_playerIDs):
  return random.choice(all_playerIDs)


def get_specific_stats(playerID):

  playerID = str(playerID)
  response = call_nhl('https://api-web.nhle.com/v1/player/'+ playerID +'/landing')
  data = response.json()

  return data


def filter_onlyNHL(teams):

  #This gets rid of non-NHL teams and None from list

  onlyNHL = []

  for team in teams:
    if team in nhl_teams:
      onlyNHL.append(team)

  return onlyNHL


def get_details(playerID, data):
  player_details = []

  firstName = data.get('firstName')
  lastName = data.get('lastName')

  player_details.append(playerID)
  player_details.append((firstName.get('default')))
  player_details[1] += " " + (lastName.get('default'))

  position = data.get('position')
  player_details.append(position)

  try:
    #incase the player was never drafted
    draft_details = data.get('draftDetails')
    draft_year = draft_details.get('year')
    player_details.append("Drafted: " + str(draft_year))
  except AttributeError:
    player_details.append('Not drafted')

  return player_details


def get_previous_teams(playerID):
  data = get_specific_stats(playerID)

  previous_teams = []

  for season in data.get('seasonTotals', []):
    
    teamCommonName = season.get('teamCommonName',{})
    
    team = teamCommonName.get('default')

    if team not in previous_teams:
      previous_teams.append(team)

  previous_teams = filter_onlyNHL(previous_teams)

  return  previous_teams


def build_playerID(season, min_teams, playerID=None):

  all_ids = get_all_playerIDs(season)

  if not playerID:
    random_player = get_random_player(all_ids)
  else:
    random_player = playerID

  previous_teams = get_previous_teams(random_player)

  while len(previous_teams) < min_teams:
    # if the current player selected does not have the min
    # number of teams we want

    # if we found a player that does not meet the required
    # number of teams, remove him from the list (n-1)
    all_ids.remove(random_player)

    random_player = get_random_player(all_ids)
    previous_teams = get_previous_teams(random_player)
  
  # If we found a player with the min numbe of teams we want
  data = get_specific_stats(random_player)
  details = get_details(random_player, data)

  return details + previous_teams


# print(get_specific_stats(random_player))
# 8478859 Niko Mikkola
# print(get_specific_stats(8478859))
# print(get_previous_teams(8478859))

# Lazy work around to finding a player that has a minimum number of teams
# I have the get player IDs which returns all the player IDs for that season
# However in my get random player, I am calling the get playerIDs method
# This lazy work around makes it so I call the api 32 times (or for however many teams and players there are in that season)
# every time I do not find a player with the minimum number of teams

# While player num of teams < min num of teams:
#   get a random player
#   print out build player id of that random player

# Black Coleman 8476399 'Devils', 'Lightning', 'Flames'

season = 20242025
min_teams = 5
print(build_playerID(season, min_teams))


# -------------- Seasonal Data Methods ---------------

def get_gameData(url, startYear, numSeasons):

  seasons = [f"{startYear+i}{startYear+i+1}" for i in range(numSeasons)]

  rows=0
  res = {}

  for s in seasons:
    response = call_nhl(url, s)

    # Try except is probably more appropriate,
    # but if it ain't broke...
    if response:
      response = response.json()
      rows+=len(response['data'])
      df = pd.json_normalize(response['data'])
      res[s] = df
      print(f"Number of games grabbed for {s} = {len(response['data'])}. Total = {rows}")
    else:
      print("ERROR: unable to connect to NHL API")
      return None

  return res

# print(get_gameData('https://api.nhle.com/stats/rest/en/team/summary', 2024,1))