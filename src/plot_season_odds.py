# coding: utf-8
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from prediction_table import playoff_odds_calc
from pprint import pprint
from nba_database.queries import team_abbreviation
from nba_database.nba_data_models import ProApiTeams

#Defining Inputs
season_year = input("Enter year: ")
try:
    season_year = int(season_year)
except ValueError:
    print("Value is not an integer. Exiting")
    sys.exit(1)

division_name = input("Enter division. Options are \n"+\
          "East: Atlantic, Central, Southeast \n"\
          "West: Southwest, Pacific, Northwest \n")

if division_name not in ['Atlantic','Central','Southeast','Southwest','Pacific','Northwest']:
    print("Invalid division name. Exiting")
    sys.exit(1)

if season_year < 2000 or season_year > 2020:
    print("Season year "+str(season_year)+" is outside of current program limits, exiting")
    sys.exit(1)
elif season_year == 2012: #Lockout year fix.
    a = datetime(season_year-1,12,25)
    b = datetime(season_year,1,15)
else:
    a = datetime(season_year-1,10,1)
    b = datetime(season_year-1,11,15)
    
end = min(datetime(season_year,4,30),datetime.today()-timedelta(days=1))


# Python Moving Average, taken by:
# https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
# note that there's a faster version using pandas but NO PANDAS.
def running_mean(x, N):
   cumsum = np.cumsum(np.insert(x, 0, 0)) 
   return (cumsum[N:] - cumsum[:-N]) / N

team_labels = [team_abbreviation(i) for i in range(1,30)]

#Team ID
#Possible divisions are Southeast, Atlantic, Central
#Pacific, Southwest, Northwest
query = ProApiTeams.select().where(ProApiTeams.division == division_name)
division_team_id_list = [i.bball_ref for i in query]


#Odds calculations
odds_list = []
x_odds = playoff_odds_calc(a,b,season_year)
x_odds = [x[0] for x in x_odds]
odds_list.append(x_odds)

dates_list=[]
dates_list.append(b)

while b < end:
    x_odds = playoff_odds_calc(a,b,season_year)
    x_odds = [x[0] for x in x_odds]
    odds_list.append(x_odds)
    dates_list.append(b)
    b = b + timedelta(days=1)
    
odds_array = np.asarray(odds_list)

plt.figure(figsize=(10,10))
plt.ylim(-5,105) #so 100 shows up on the graph, and 0 (thanks V.)

#Get team data
for team_id_db in division_team_id_list:
    team_id=team_id_db-1
    team_data = odds_array[:,team_id]
    N = len(team_data)
    average_count = 5
    average_team_data = running_mean(team_data,average_count)
    average_dates_list = dates_list[average_count-1:]
    #plt.plot(dates_list,team_data)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
    plt.plot(average_dates_list,average_team_data, label=team_abbreviation(team_id+1), alpha = 0.6)

plt.xlabel('Date')
plt.ylabel('Team Playoff Odds')
plt.title(division_name+' Division Playoff Odds '+str(season_year-1)+'-'+str(season_year))
plt.legend()
plt.xticks(rotation=15)
plt.savefig(division_name+'_'+str(season_year)+'.png')
plt.show()
