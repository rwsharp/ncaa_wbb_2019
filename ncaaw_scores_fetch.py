#!/bin/python
#this is a python 2 script
from lxml import html
import requests
import pandas
import sys

#output_path = 'data/wbb_games_20190310.html'
output_path = 'data/wbb_games_' + str(sys.argv[2]) + '.html'#use with input wrapper, second sys.argv is the human-readable version of the date

# Download and save the page (RICH'S ORIGINAL)
# url = 'https://stats.ncaa.org/season_divisions/16720/scoreboards?utf8=%E2%9C%93&season_division_id=&game_date=03%2F11%2F2019&commit=Submit'
# page = requests.get(url)
# with open(output_path, 'w') as output_file:
#    print >> output_file, page.content

# Download and save the page (PAT LOOPING WITH SYS INPUT)
url = 'https://stats.ncaa.org/season_divisions/16720/scoreboards?utf8=%E2%9C%93&season_division_id=&game_date=' + str(sys.argv[1]) + '&commit=Submit' #build URL string with URL encoded date (sys.argv 1)
page = requests.get(url)
with open(output_path, 'w') as output_file:
    print >> output_file, page.content

# Read a saved page from file
with open(output_path, 'r') as input_file:
    page = input_file.read()

tree = html.fromstring(page)
xpath = '//*[@id="contentarea"]/table/tbody'
tr_elements = tree.xpath('//tr')

for row_num, tr in enumerate(tr_elements[1:]):
    subrow = row_num % 5
    if subrow == 0:
        print('----------')
    td_elements = tr.xpath('td')
    for col_num, td in enumerate(td_elements):
        if (subrow, col_num) in ((0,0), (0,2), (0,4), (0,5), (3,1), (3,2)):
            print('{}:{}:{}'.format(subrow, col_num, td.text_content().strip()))
