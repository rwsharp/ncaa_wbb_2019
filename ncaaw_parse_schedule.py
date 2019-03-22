#!/bin/python
#this is a python 2 script that is used with a shell wrapper to take an input HTML file from stats.ncaa.org.  URL pattern is: stats.ncaa.org/team/[teamcode]/14320 - where 14320 means "women's basketball" and the teamcode varies by school.
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
team_code_str = input_path.replace("data/team_schedules/", "")
team_code = team_code_str.replace(".html", "")

#load the html file into lxml's parsing function
tree = html.fromstring(page)

#define xpath of the team name (inside the second h1 element)
teamname_element = tree.xpath('//h1')[1]
#regex to split the team record away from the team name
teamname_str = re.search('(.*)\(.*\)', teamname_element.text_content())
#take only the first result group of the regex in previous line
teamname = teamname_str.groups()[0].strip()
#no-space find-and-replace version of name to use in filenames
teamname_nospace = teamname.replace(" ", "_")

#extract the games table from the html
table_str = page.split('grey_heading') #splits the html file on 'grey_heading, since the results table starts after the 2nd one.  Needed because there are an unknown number of rows BEFORE the scores start.'
table_group = table_str[2] #chop and take the 3rd group
table = html.fromstring(table_group) #load into lxml
tr_elements = table.xpath("//tr[not(contains(@id,'off_def_row'))]") #take all rows EXCEPT NCAA's weird hidden rows

#define the dictionary that will be later loaded into the dataframe. each column needs to have a key value pair defined here.  Order doesn't matter here.
data = {
        'gamedate': list(),
        'guest': list(),
        'result': list(),
        'FGM': list(),
        'FGA': list(),
        '3FG': list(),
        '3FGA': list(),
        'FT': list(),
        'FTA': list(),
        'home_points': list()
    }

#loop over all the rows in the extracted game table starting with the 38th because there's a LOT of crap at the top of that table.

#print to StdOut for debugging purposes
#for row_num, tr in enumerate(tr_elements):
#    subrow = row_num % 1
#    if subrow == 0:
#        print('----------')
#    td_elements_list = tr.xpath('td')
#    for col_num, td in enumerate(td_elements_list):
#        if (subrow, col_num) in ((0,0), (0,1), (0,2), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10)):
#            print('{}'.format(td.text_content().strip()))

for row_num, tr in enumerate(tr_elements):
    subrow = row_num % 1
#loop over the cells in the row
    td_elements = tr.xpath('td')
#define what each row is for the dict (skipipng column #4 because "minutes played in the game" is not useful)
    for col_num, td in enumerate(td_elements):
        if (subrow, col_num) == (0, 0):
            data['gamedate'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 1):
            data['guest'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 2):
            data['result'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 4):
            data['FGM'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 5):
            data['FGA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 6):
            data['3FG'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 7):
            data['3FGA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 8):
            data['FT'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 9):
            data['FTA'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 10):
            data['home_points'].append(td.text_content().strip())

#define output file path
csv_output_file = 'data/team_schedules/'+ str(team_code) + '-' + str(teamname_nospace) + '.csv'

#load into dataframe
data = pandas.DataFrame.from_dict(data)

#append team name column to the dataframe
data['teamname'] = teamname

#output to csv
data.to_csv(csv_output_file, index=False)
