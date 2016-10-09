#-*-coding:utf8;-*-
#qpy:2
#qpy:console

print('Advanced Stats Moving Average Calculator')

app_dir='/home/martin/naismith/'
folder=app_dir+'v1.0_dev/db_folder/'
dbname='nba_data_test.sqlite'
new_table_name='pro_api_asma'


import sys
import numpy as np
import sqlite3
from pprint import pprint
from moving_averages import runningMeanFast

import sys
sys.path.append(app_dir+'v1.0_dev/pro_api_tools//')
from proballapi_library import get_advanced_data

import sys
sys.path.append(app_dir+'v1.0_dev/python_db_tools/')
from dbtools import table_initializer

#const
games_to_avg=15 #one month


conn=sqlite3.connect(folder+dbname)
c=conn.cursor()


#Define some queries
query='SELECT team_id FROM pro_api_teams'
str_input=query
teamset=c.execute(str_input).fetchall()
teamset=[t[0] for t in teamset]

#season we are working with
season=raw_input('Please enter a season to process: ')

#Stats to be queried for and 
#moving averaged aka the four factors
#shooting and ft (combined into efg) - 1
#rebounding (off and def) - 2,3
#turnovers - 4

#debug tool - run through one team and not 30
teamset=[1610612765]

#List to store season advanced data
season_adv_data=[]

for t in teamset:
    print('processing team '+str(t))

    query='select pro_api_games.id, pro_team_adv_stats.efg_pct, pro_team_adv_stats.oreb_pct, pro_team_adv_stats.dreb_pct, pro_team_adv_stats.tm_tov_pct\
           from pro_team_adv_stats inner join pro_api_games on \
           (pro_team_adv_stats.game_id=pro_api_games.id) \
           where pro_api_games.season='+str(season)+' and pro_team_adv_stats.team_id='+str(t)+';'
    str_input=query
    dataset=c.execute(str_input).fetchall()
    
    #If dataset length is 0 (i.e. no games found) end program early
    if len(dataset)==0:
      sys.exit('No games found for season requested, exiting program')
   
    #pprint(dataset)
    
    #Opposition stats query - TO DO
    query='select pro_api_games.id, pro_team_adv_stats.efg_pct, pro_team_adv_stats.oreb_pct, pro_team_adv_stats.dreb_pct, pro_team_adv_stats.tm_tov_pct\
           from pro_team_adv_stats inner join pro_api_games on \
           (pro_team_adv_stats.game_id=pro_api_games.id) \
           where pro_api_games.season='+str(season)+' and pro_team_adv_stats.opponent_id='+str(t)+';'
    str_input=query
    oppo_dataset=c.execute(str_input).fetchall()
    
    #pprint(oppo_dataset)
    
    #Defining first column of array.
    games_list=[d[0] for d in dataset]
    team_array=np.zeros((len(games_list),9))
    team_array[:,0]=games_list
    
    #pprint(team_array)
    
    
    #Do running averages
    dataset=np.asarray(dataset)
    oppo_dataset=np.asarray(oppo_dataset)
	
	################
    ###Team stats###
	################
    for i in range(1,5):
    
      #fill in first few entries as required
      #with original values
      for j in range(0,games_to_avg):
        team_array[j,i]=dataset[j,i]
     
      
      means=runningMeanFast(dataset[:,i],games_to_avg)
      
      #trim end of means to deal with moving averages of less than games_to_avg
      #shift averages to the right, link to games to the left
      means=means[:len(means)-games_to_avg+1]
        
      #This does!
      for j in range(games_to_avg,len(means)+games_to_avg-1): # necessary to fill array completely
        team_array[j,i]=means[j-games_to_avg]
	
    print(team_array)
    print(len(team_array))
	####################
	###Opponent stats###
    ####################
	
    for i in range(5,9):
    
      #fill in first few entries as required
      #with original values
      for j in range(0,games_to_avg):
        #print(oppo_dataset[j,i-4])
        team_array[j,i]=oppo_dataset[j,i-4] #-4 for oppo dataset
     
      means=runningMeanFast(oppo_dataset[:,i-4],games_to_avg)
      
      #trim end of means to deal with moving averages of less than games_to_avg
      #shift averages to the right, link to games to the left
      means=means[:len(means)-games_to_avg+1]
        
      #This does!
      for j in range(games_to_avg,len(means)+games_to_avg-1): #1 necessary to fill array completely
        team_array[j,i]=means[j-games_to_avg]
      
    print(team_array)
    print(len(team_array))           
      
    #create dict
    headers=['game_id','efg_pct','oreb_pct','dreb_pct','tm_tov_pct',\
                         'o_efg_pct','o_oreb_pct','o_dreb_pct','o_tm_tov_pct','team_id']
    team_list=team_array.tolist()
      
    for stats in team_list:
      stats.append(t)

    team_list=[dict(zip(headers,s)) for s in team_list]
      
    #Cleanups
    for stats in team_list:
      stats['game_id']=int(stats['game_id'])
      stats['id']=stats['game_id']*1000+stats['team_id']%1000 #only the last three digits are unique
      season_adv_data.append(stats)  
      
    #pprint(team_list)
      
conn.close()


pprint(season_adv_data[0])
#Create database using season advanced data
table_initializer(folder+dbname,new_table_name,season_adv_data[0],season_adv_data)

