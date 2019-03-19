
# coding: utf-8

# In[1]:

import glob
import os
import re
import datetime
import numpy as np
import pandas as pd
import scipy.stats


# In[2]:

# NCAA women's RPI: https://www.ncaa.com/rankings/basketball-women/d1/ncaa-womens-basketball-rpi


# In[3]:

data_files = glob.glob(os.path.expanduser('~/Dropbox/Uncertain Principles/Articles/NCAAWomen2019/data/*csv'))

print('Number of game files: {}'.format(len(data_files)))

game_data = None
file_dates = list()
for data_file in data_files:
    m = re.search('.*(\d\d-\d\d-\d\d\d\d).csv', data_file)
    if m is not None:
        file_date = datetime.datetime.strptime(m.groups()[0], '%m-%d-%Y').date()
        file_dates.append(file_date)
    
    df = pd.read_csv(data_file)
    
    if game_data is None:
        game_data = df
    else:
        game_data = game_data.append(df)

game_data.reset_index(drop=True, inplace=True)
    
print('Number of individual games: {}'.format(game_data.shape[0]))
print('Most recent file date: {}'.format(max(file_dates)))


# In[4]:

left = game_data[['guest', 'gametime']].groupby('guest').count().reset_index()
right = game_data[['home', 'gametime']].groupby('home').count().reset_index()

df2 = left.merge(right, left_on='guest', right_on='home')
df2['n_games'] = df2['gametime_x'] + df2['gametime_y']

n_d1_teams = df2[['home', 'n_games']][df2['n_games'] > 20].shape[0]

print('Number of D1 teams in data: {}'.format(n_d1_teams))

teams = df2[['home']][df2['n_games'] > 20].rename(index=str, columns={'home': 'name'})
teams.reset_index(inplace=True, drop=True)
teams.reset_index(inplace=True)

# Example: get the index of a team by name
# int(teams.index[teams['name'] == 'Air Force'].tolist()[0])

teams.head()


# In[5]:

game_data['spread'] = game_data['home_score'] - game_data['guest_score']

game_data = game_data.merge(teams, left_on='guest', right_on='name').rename(index=str, columns={'index': 'guest_index'})                      .drop('name', axis=1)
game_data = game_data.merge(teams, left_on='home', right_on='name').rename(index=str, columns={'index': 'home_index'})                      .drop('name', axis=1)

game_data.head()


# In[6]:

# set some constants
tau = 4.26
sig = 11 
h   = 4

# code to compute the probability that one team is better than another based on point spread, x.
# compute P(Z>0 | X=x) from eq. (12) pnorm(2*tau^2/(sig*sqrt((sig^2+2*tau^2)*(sig^2+4*tau^2)))*x - h/sig*sqrt((sig^2+4*tau^2)/(sig^2+2*tau^2))) 
a = 2*(tau**2)/(sig*np.sqrt(((sig**2)+2*(tau**2))*((sig**2)+4*(tau**2))))
b = 2*(tau**2)*h/(sig*np.sqrt(((sig**2)+2*(tau**2))*((sig**2)+4*(tau**2))))


# In[7]:

t = np.zeros((n_d1_teams, n_d1_teams))
teams['ngames'] = 0

for k, row in game_data.iterrows():
    try:
        i = int(row['home_index'])
        j = int(row['guest_index'])
        spread = row['spread']

        if not np.isnan(spread):
            # Sometimes a gametime is posted before the score is known in the data
            # This leads to an undefined spread
            # Skip for now and hope the score is captured in a later update
            
            teams.loc[teams['index'] == i, 'ngames'] += 1
            teams.loc[teams['index'] == j, 'ngames'] += 1

            r = scipy.stats.norm.cdf(a*spread-b)    
            t[i,j] = t[i,j] + (1.0 - r)
            t[j,i] = t[j,i] + r
            t[i,i] = t[i,i] + r
            t[j,j] = t[j,j] + (1.0 - r)
    except:
        print(i, j, spread, row['home'], row['guest'], row['gametime'], r)
        raise
    


# In[8]:

for i in range(n_d1_teams):
    t[i] = t[i] / float(teams[teams['index'] == i]['ngames'])


# In[9]:

#initialize ranking procedure
p = np.zeros((1, n_d1_teams))

z = float(np.sum(range(1, n_d1_teams+1)))
for i in range(n_d1_teams):
    p[0, i] = (n_d1_teams - i)/z


# In[10]:

# run ranking procedure
for itr in range(1000):
    p_next = np.matmul(p, t)
    if(itr % 100 == 0):
        print(np.linalg.norm(p_next - p))
    p = p_next


# In[11]:

teams[teams['index'] == np.argmax(p)]


# In[12]:

rank = pd.DataFrame({'LRMC': p[0], 'team_index': range(n_d1_teams)})
rank['LRMC_rank'] = rank['LRMC'].rank(ascending=False)
rank = rank.merge(teams, left_on='team_index', right_on='index', how='left')
rank[rank['LRMC_rank'] <= 25].sort_values('LRMC_rank')

