from lxml import html
import pandas

with open(>>>>>PATH_TO_THE_DOWNLOADED_HTML_FILE<<<<<<, 'r') as input_file:
    page = input_file.read()

tree = html.fromstring(page)
teamxpath =  '//h1'[1]
teamname = tree.teamxpath.text_content().strip()

xpath = '//*[@id="game_breakdown_div"]/table/table'
tr_elements = tree.xpath('//tr')

data = {
        'teamname': list(),
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

for row_num, tr in enumerate(tr_elements[1:]):
    subrow = row_num % 2
    if subrow == 0:
        print('----------')
    td_elements = tr.xpath('td')
    for col_num, td in enumerate(td_elements):
        if (subrow, col_num) in ((0,0), (0,1), (0,2), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10)):
            print('{}'.format(td.text_content().strip()))

        if (subrow, col_num) == (0, 0):
            data['teamname'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 1):
            data['gamedate'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 2):
            data['guest'].append(td.text_content().strip())
        elif (subrow, col_num) == (0, 3):
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

csv_output_path = output_path = 'data/team_schedules/' + str(sys.argv[2]) + '.csv'
data = pandas.DataFrame.from_dict(data)
data.to_csv(csv_output_path, index=False)