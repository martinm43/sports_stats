 

import os
wkdir = os.path.dirname(os.path.realpath(__file__))+'/'

def standings_generation():
  execfile(wkdir+'nba_api_team_indexer.py')
  execfile(wkdir+'season_games_splitter.py')
  execfile(wkdir+'analytics/ptsaverages.py')
  execfile(wkdir+'ratings_calculations.py')
  execfile(wkdir+'monte_carlo_calculations.py')

if __name__=='__main__':
    standings_generation()    

