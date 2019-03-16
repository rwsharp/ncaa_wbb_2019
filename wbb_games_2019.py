from lxml import html
import requests
import pandas
import re
import os
import glob


def get_game_data(year, month, day, output_path):
    # Download and save the page
    # day and month must be zero padded
    # year must be four digits

    # example output_path: 'data/wbb_games_20190310.html'
    url = 'https://stats.ncaa.org/season_divisions/16720/scoreboards?utf8=%E2%9C%93&season_division_id=&game_date={}%2F{}%2F{}&commit=Submit'.format(month, day, year)
    page = requests.get(url)
    with open(output_path, 'w') as output_file:
       print >> output_file, page.content


def get_data(data_path):
    # Read a saved page from file
    with open(data_path, 'r') as input_file:
        page = input_file.read()

    tree = html.fromstring(page)
    tr_elements = tree.xpath('//tr')

    data = {
        'gametime': list(),
        'guest': list(),
        'guest_score': list(),
        'location': list(),
        'home': list(),
        'home_score': list()
    }

    for row_num, tr in enumerate(tr_elements[1:]):
        subrow = row_num % 5
        if subrow == 0:
            1
            # print('----------')

        td_elements = tr.xpath('td')

        for col_num, td in enumerate(td_elements):
            if (subrow, col_num) == (0, 0):
                data['gametime'].append(td.text_content().strip())
            elif (subrow, col_num) == (0, 2):
                data['guest'].append(td.text_content().strip())
            elif (subrow, col_num) == (0, 4):
                data['guest_score'].append(td.text_content().strip())
            elif (subrow, col_num) == (0, 5):
                data['location'].append(td.text_content().strip())
            elif (subrow, col_num) == (3, 1):
                data['home'].append(td.text_content().strip())
            elif (subrow, col_num) == (3, 2):
                data['home_score'].append(td.text_content().strip())

    data = pandas.DataFrame.from_dict(data)

    return data


data_path = '/Users/rsharp/Dropbox/Uncertain Principles/Articles/NCAAWomen2019/data'
file_names = glob.glob('{}/*.html'.format(data_path))

for k, file_name in enumerate(sorted(file_names)):
    csv_output_path = re.sub('html$', 'csv', file_name)
    df = get_data(file_name)
    print('writing {}'.format(os.path.basename(csv_output_path)))
    df.to_csv(csv_output_path, index=False)
