#!/bin/python
#this is a python 2 script that is used with a shell wrapper to take an input HTML file from stats.ncaa.org.  URL pattern is: stats.ncaa.org/team/[teamcode]/stats/14320 - where 14320 means "women's basketball" and the teamcode varies by school.
from lxml import html
import requests
import re
import pandas
import sys

input_path = sys.argv[1]#use with input wrapper, second sys.argv is the human-readable version of the date

# Read a saved page from file
with open(input_path, 'r') as input_file:
    page = input_file.read()

#define team code as used by NCAA by stripping it out of the input file name
team_code_str = input_path.replace("data/team_stats/", "")
team_code = team_code_str.replace(".html", "")

#load the html file into lxml's parsing function
tree = html.fromstring(page)

#define xpath of the team name (inside the first legend element)
teamname_element = tree.xpath('//legend//a')[0]
teamname = teamname_element.text_content()
#no-space find-and-replace version of name to use in filenames
teamname_nospace = teamname.replace(" ", "_")

#extract the games table from the html
tr_elements = tree.xpath("//tr[@class='text']") #take all rows with class 'text'

#define the dictionary that will be later loaded into the dataframe. each column needs to have a key value pair defined here.  Order doesn't matter here.
data = {
        'jersey': list(),
        'player_name': list(),
        'year': list(),
        'position': list(),
        'height': list(),
        'GP': list(),
        'GS': list(),
        'minutes': list(),
        'FGM': list(),
        'FGA': list(),
        'FG%': list(),
        '3FG': list(),
        '3FGA': list(),
        '3FG%': list(),
        'FT': list(),
        'FTA': list(),
        'FT%': list(),
        'PTS': list(),
        'PPG': list(),
        'ORebs': list(),
        'DRebs': list(),
        'Tot_rebs': list(),
        'Avg_rebs': list(),
        'AST': list(),
        'TO': list(),
        'STL': list(),
        'BLK': list(),
        'PF': list()
    }

#loop over all the rows in the extracted game table excepting the last one because that's the team totals

#print to StdOut for debugging purposes
#for row_num, tr in enumerate(tr_elements[:-1]):
#    subrow = row_num % 1
#    if subrow == 0:
#        print('----------')
#    td_elements_list = tr.xpath('td')
#    for col_num, td in enumerate(td_elements_list):
#        if (subrow, col_num) in ((0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10), (0,11), (0,12), (0,13), (0,14), (0,15), (0,16), (0,17), (0,18), (0,19), (0,20), (0,21), (0,22), (0,23), (0,24), (0,25), (0,26), (0,27)):
#            print('{}'.format(td.text_content().strip()))

for row_num, tr in enumerate(tr_elements[:-1]):
    subrow = row_num % 1
#loop over the cells in the row
    td_elements = tr.xpath('td')
#define what each row is for the dict (skipipng column #4 because "minutes played in the game" is not useful)
    for col_num, td in enumerate(td_elements):
        if (subrow, col_num) == (0, 0):
            data['jersey'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 1):
            data['player_name'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 2):
            data['year'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 3):
            data['position'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 4):
            data['height'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 5):
            data['GP'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 6):
            data['GS'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 7):
            data['minutes'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 8):
            data['FGM'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 9):
            data['FGA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 10):
            data['FG%'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 11):
            data['3FG'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 12):
            data['3FGA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 13):
            data['3FG%'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 14):
            data['FT'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 15):
            data['FTA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 16):
            data['FT%'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 17):
            data['PTS'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 18):
            data['PPG'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 19):
            data['ORebs'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 20):
            data['DRebs'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 21):
            data['Tot_rebs'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 22):
            data['Avg_rebs'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 23):
            data['AST'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 24):
            data['TO'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 25):
            data['STL'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 26):
            data['BLK'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 27):
            data['PF'].append(td.text_content().strip())

#define output file path
csv_output_file = 'data/team_stats/'+ str(team_code) + '-' + str(teamname_nospace) + '.csv'

#load into dataframe
data = pandas.DataFrame.from_dict(data)

#append team name column to the dataframe
data['teamname'] = teamname

#output to csv
data.to_csv(csv_output_file, index=False)
