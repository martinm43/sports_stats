#-*-coding:utf8;-*-
#qpy:2
#qpy:console

#Choose working directory.
from .nba_data_models import BballrefScores as Game
import time, datetime
import numpy as np

###################
# Time Conversion #
###################

def epochtime(datetime_obj):
  """
  Convert time in MON DAY YEAR format to a UNIX timestamp
  """
  return time.mktime(datetime_obj.timetuple())

def prettytime(timestamp):
  """
  Convert time since epoch to date
  """
  return datetime.datetime.fromtimestamp(timestamp)

#####################
# String Conversion #
#####################

def team_abbreviation(team_alphabetical_id):
    """
    Converts team numerical ids into team names.
    """
    from .nba_data_models import ProApiTeams
    s_query = ProApiTeams.select(ProApiTeams.abbreviation).\
      where(ProApiTeams.bball_ref == team_alphabetical_id)
    s_result = s_query[0]
    return s_result.abbreviation

def full_name_to_id(full_team_name):
    """
    Converts 'normal team names', provides the rest of the data needed for processing 
    Team id
    """
    if full_team_name == "New Jersey Nets":
        full_team_name = "Brooklyn Nets"
    if full_team_name == "Seattle SuperSonics":
        full_team_name = "Oklahoma City Thunder"
    if full_team_name == "Washington Bullets":
        full_team_name = "Washington Wizards"
    if full_team_name == "Vancouver Grizzlies":
        full_team_name = "Memphis Grizzlies"
        
    from .nba_data_models import ProApiTeams
    s_query = ProApiTeams.select(ProApiTeams.bball_ref).\
      where(ProApiTeams.full_team_name == full_team_name)

    s_result = s_query[0]
    return s_result.bball_ref

def abbrev_to_id(team_abbrev):
    """
    Converts 'normal team names', provides the rest of the data needed for processing 
    Team id
    """
    from .nba_data_models import ProApiTeams
    s_query = ProApiTeams.select(ProApiTeams.bball_ref).\
      where(ProApiTeams.abbreviation == team_abbrev)
    s_result = s_query[0]
    return s_result.bball_ref

def id_to_name(team_id):
    """
    Converts 'normal team names', provides the rest of the data needed for processing 
    Team id
    """
    from .nba_data_models import ProApiTeams
    s_query = ProApiTeams.select(ProApiTeams.team_name).\
      where(ProApiTeams.bball_ref == team_id)
    s_result = s_query[0]
    return s_result.team_name

################################
# Getting Information On Games #
################################

def games_query(start_datetime,end_datetime):
    """
    Input: datetime objects
    Output: [away_team, away_pts, home_team, home_pts] list
    """
    start_epochtime=epochtime(start_datetime)
    end_epochtime=epochtime(end_datetime)
    played_games = Game.select().where(
        Game.datetime < end_epochtime,
        Game.datetime > start_epochtime,
        Game.away_pts > 0).order_by(Game.datetime)

    played_games = [[g.away_team_id, g.away_pts, g.home_team_id, g.home_pts]
                    for g in played_games]
    return played_games

def season_query(season_year):
    """
    Input: a season year
    Output: [away_team, away_pts, home_team, home_pts] list
    """

    played_games = Game.select().where(Game.season_year == season_year,
                                       Game.away_pts > 0).order_by(Game.datetime)

    played_games = [[g.away_team_id, g.away_pts, g.home_team_id, g.home_pts, g.datetime, season_year]
                        for g in played_games]

    return played_games

def games_won_query(played_games,return_format="list"):
    """
    Input: [away_team, away_pts, home_team, home_pts] list
    Output: a list of lists, a list, or a matrix
    """
    winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
    winrows = []
    if return_format == 'list_of_lists':
        winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
        winrows = []
        for i in range(1, 31):
            winrows.append([winlist.count(i)])
        return_value = winrows
    elif return_format == 'list':
        winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
        winrows = []
        for i in range(1, 31):
            winrows.append(winlist.count(i))
        return_value = winrows
    elif return_format == 'matrix':
        win_matrix = np.zeros((30, 30))
        for x in played_games:
            if x[1] > x[3]:
                win_matrix[x[0] - 1, x[2] - 1] += 1
            elif x[3] > x[1]:
                win_matrix[x[2] - 1, x[0] - 1] += 1
        return win_matrix
    else:
        print('invalid option')
        return_value = 0
    return return_value

def future_games_query(season_datetime, season_year):
    season_epochtime = epochtime(season_datetime)
    query = Game.select().where(Game.datetime>=season_epochtime,\
                                Game.season_year==season_year)
    matches = [[x.away_team_id,x.home_team_id] for x in query]
    return matches

#############################################
# Getting ratings for a given team
#############################################
def team_elo_rating(team_id,epochtime):
    """
    Get the most recent Elo rating for a team given a date and the team_id

    Parameters
    ----------
    team_id : integer team ID 1-30
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    rtg : most recent Elo rating

    """
    from .nba_data_models import NbaTeamEloData
    rtg_iterable = NbaTeamEloData.select().where(NbaTeamEloData.team_id == team_id,\
                    NbaTeamEloData.datetime < epochtime).order_by(NbaTeamEloData.datetime.desc()).limit(1)
    rtg = [x.elo_rating for x in rtg_iterable]
    rtg = rtg[0]
    return rtg

def elo_ratings_list(epochtime):
    """
    

    Parameters
    ----------
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    ratings_list : list of most recent team ratings to date

    """
    ratings_list =[]
    for i in range(1,31):
        ratings_list.append(team_elo_rating(i,epochtime))
    return ratings_list
        
