#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for calculating what the "difference over sum" distribution looks like
for the NBA, for later use in mathematical modelling.

Inputs:
    None (reads from database)
    
Outputs:
    None (prints mean and standard deviation of logistic distribution fitted)

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
#from sklearn.preprocessing import StandardScaler

from nba_database.nba_data_models import BballrefScores

# Get minimum and maximum years for the distribution fitting
x = BballrefScores.select().order_by(BballrefScores.season_year.asc()).get()
min_val = x.season_year
x = BballrefScores.select().order_by(BballrefScores.season_year.desc()).get()
max_val = x.season_year

z = BballrefScores.select().where(BballrefScores.season_year >= min_val, BballrefScores.season_year < max_val)
mov = [x.home_pts-x.away_pts for x in z]
dos = [(x.home_pts-x.away_pts)/(x.home_pts+x.away_pts) for \
                 x in z if x.home_pts+x.away_pts > 0]


#monitored_variable = pd.DataFrame(dos)
monitored_variable = dos
#description = monitored_variable.describe()
#print(description)

size = len(monitored_variable)

df_fit = np.asarray(monitored_variable)

dist_name = 'logistic'

#Fitting distribution
dist = getattr(stats,dist_name)
parameters = dist.fit(df_fit)
mean = parameters[0]
stddev = parameters[1]

mean_str = "%.5f" % mean
stddev_str = "%.5f" % stddev




plt.hist(monitored_variable, bins=20, density=True, color='g')
 
# Get plot limits.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = dist.pdf(x, mean, stddev)
plt.plot(x, p, 'k', linewidth=2)
title = dist.name+" fit results: mu = %.5f,  std = %.5f" % (mean, stddev)
print(title)
plt.title(title)

plt.show()
plt.savefig("fit_figure.png")