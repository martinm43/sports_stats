#-*-coding:utf8;-*-
#qpy:2
#qpy:console


app_dir='/home/martin/naismith/'

db_folder=app_dir+'v1.0_dev/db_folder/'
dbname='nba_data_test.sqlite'
new_table_name='bballref_avg_pts_diff'


import sys
import numpy as np
import sqlite3
from pprint import pprint

#analytics libraries in current folder
from moving_averages import runningMeanFast

import sys
sys.path.append(app_dir+'v1.0_dev/python_db_tools/')
from dbtools import table_initializer

#const
games_to_avg=5 #one week

conn=sqlite3.connect(db_folder+dbname)
c=conn.cursor()

#Define some queries
'1 to 30'
teamset=[t for t in range(1,31)]
print(teamset)

#season we are working with
season=raw_input('Please enter a season to process: ')

#Only need point differential

#debug tool - run through one team and not 30
teamset=[28]

#List to store season advanced data
season_pts_data=[]

for t in teamset:
    print('processing team '+str(t))

    query='select id,away_team_id, away_pts, home_team_id, home_pts from bballref_scores\
           where (away_team_id='+str(t)+' OR home_team_id='+str(t)+') AND season_year='+str(season)+';'
    str_input=query
    dataset=c.execute(str_input).fetchall()
    
    
    #If dataset length is 0 (i.e. no games found) end program early
    if len(dataset)==0:
      print('No games found for season '+str(season)+' and team '+str(t)+', be careful - is this ok?')
      continue
    
    games_list=[d[0] for d in dataset]
    diff_array=np.zeros((len(games_list),2))
    diff_array[:,0]=[d[0] for d in dataset]
    
    #calculate point differentials as required
    #this can be done as a conditional list comprehension
    diff_vector=[d[2]-d[4] if d[1]==t else d[4]-d[2] for d in dataset]
    #pprint(diff_vector)
    team_vector=np.asarray(diff_vector)
    
    
    #Do running averages
    dataset=np.asarray(diff_vector)
    means=runningMeanFast(dataset,games_to_avg)
      
    #trim end of means to deal with moving averages of less than games_to_avg
    #shift averages to the right, link to games to the left
    means=means[:len(means)-games_to_avg+1]
        
      #This does!
    for j in range(games_to_avg,len(means)+games_to_avg-1): # necessary to fill array completely
      team_vector[j]=means[j-games_to_avg]
	
    print(len(team_vector))
    for t in team_vector:
      if t > 20:
	t=20
      if t<-20:
	t=-20
    print(team_vector)
	
    diff_array[:,1]=team_vector


      #create dict
    headers=['game_id','p_diff','team_id']
    team_list=diff_array.tolist()
      
    for stats in team_list:
      stats.append(t)

    #print(team_list)

    team_list=[dict(zip(headers,s)) for s in team_list]
      
    #Cleanups
    for stats in team_list:
      stats['game_id']=int(stats['game_id'])
      #p#rint(stats['team_id']%1000)
      stats['id']=stats['game_id']*100+stats['team_id'] 
      #print(stats['id'])
      season_pts_data.append(stats)  
      
      #pprint(team_list)
      
conn.close()

#Create database using season advanced data
table_initializer(db_folder+dbname,new_table_name,season_pts_data[0],season_pts_data)
