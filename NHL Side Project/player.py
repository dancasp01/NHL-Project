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
  "VGK"   # Vegas Golden Knights
]

nhl_teams = [
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

  startSeason = 20232024
  endSeason = 20232024

  if start:
    startSeason = start

  if end:
    endSeason = end
  
  if endSeason < startSeason:
    return "End season cannot be befor start season"

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
    ('cayenneExp', f'gameTypeId=2 and seasonId<={endSeason} and seasonId>={startSeason}'),
  )
  
  # Call API with given headers and parameters
  response = requests.get(url, headers=headers, params=params)

  return response

# -------------- Data Methods ---------------

def get_playerIDs():

  forwards = []
  defensemen = []
  goalies = []

  for team in team_abreviations:

    response = call_nhl('https://api-web.nhle.com/v1/roster/'+ team + '/20232024')

    data = response.json()

    forwards_data = list(data['forwards'])
    defensemen_data = list(data['defensemen'])
    golies_data = list(data['goalies'])

    for forward_player in forwards_data:
      forwards.append(forward_player['id'])

    for defense_player in defensemen_data:
      defensemen.append(defense_player['id'])

    for goalie in golies_data:
      goalies.append(goalie['id'])

  return [forwards, defensemen, goalies]


def get_random_player():
  playerIDs = get_playerIDs()

  fdg = random.randint(0,2)

  if not fdg:
    print('Forward')
  elif fdg == 1:
    print('Defenseman')
  else:
    print('Goalie')

  random_player = playerIDs[fdg]

  return random.choice(random_player)


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


  try:
    #incase the player was never drafted
    draft_details = data.get('draftDetails')
    draft_year = draft_details.get('year')
    player_details.append("Drafted: " + str(draft_year))
  except AttributeError:
    player_details.append('Not drafted')

  return player_details


def build_playerID(playerID):
  data = get_specific_stats(playerID)

  details = get_details(playerID, data)

  previous_teams = []

  for season in data.get('seasonTotals', []):
    
    teamCommonName = season.get('teamCommonName',{})
    
    team = teamCommonName.get('default')

    if team not in previous_teams:
      previous_teams.append(team)


  previous_teams = filter_onlyNHL(previous_teams)

  return details + previous_teams


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

random_player = get_random_player()
# print(get_specific_stats(random_player))
# 8478859 Niko Mikkola
print(build_playerID(random_player))