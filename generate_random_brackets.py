import glob
import os
import re
import datetime
import numpy
import pandas
import scipy.stats
import argparse
import itertools

#data_path = '~/Dropbox/Uncertain Principles/Articles/NCAAWomen2019/data'
#data_path_pattern = '~/Dropbox/Uncertain Principles/Articles/NCAAWomen2019/data/*csv'

def read_data(data_path):
    data_path_pattern = os.path.join(data_path, '*csv')
    data_files = glob.glob(os.path.expanduser(data_path_pattern))

    print('Number of game files: {}'.format(len(data_files)))

    game_data = None
    file_dates = list()
    for data_file in data_files:
        m = re.search('.*(\d\d-\d\d-\d\d\d\d).csv', data_file)
        if m is not None:
            file_date = datetime.datetime.strptime(m.groups()[0], '%m-%d-%Y').date()
            file_dates.append(file_date)

        df = pandas.read_csv(data_file)

        if game_data is None:
            game_data = df
        else:
            game_data = game_data.append(df)

    # There are a few duplicate rows. Drop duplicates to be safe.
    game_data = game_data.drop_duplicates()

    game_data.reset_index(drop=True, inplace=True)

    print('Number of individual games: {}'.format(game_data.shape[0]))
    print('Most recent file date: {}'.format(max(file_dates)))

    return game_data


def get_teams(game_data):
    left = game_data[['guest', 'gametime']].groupby('guest').count().reset_index()
    right = game_data[['home', 'gametime']].groupby('home').count().reset_index()

    df2 = left.merge(right, left_on='guest', right_on='home')
    df2['n_games'] = df2['gametime_x'] + df2['gametime_y']

    n_d1_teams = df2[['home', 'n_games']][df2['n_games'] > 20].shape[0]

    print('Number of D1 teams in data: {}'.format(n_d1_teams))

    teams = df2[['home']][df2['n_games'] > 20].rename(index=str, columns={'home': 'name'})
    teams.reset_index(inplace=True, drop=True)
    teams.reset_index(inplace=True)

    return teams


def parse_cl():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data-path',   help='path where html versions of score data is located (sourced from https://stats.ncaa.org/season_divisions/16720/scoreboards')
    parser.add_argument('--output-path', help='path to write randomized brackets')
    parser.add_argument('--n-trials', default=1, type=int, help='number of trials to run')
    parser.add_argument('--shots',               type=int, help='max number of luck shots, e.g., 3')
    parser.add_argument('--pm',       nargs='+', type=int, help='miss / max portions, e.g., (3, 2)')
    parser.add_argument('--points',   nargs='+', type=int, help='free throw/two-pts/three-pts portions, e.g., (1, 5, 2)')
    args = parser.parse_args()

    return args

def add_spread(game_data, teams):
    game_data['spread'] = game_data['home_score'] - game_data['guest_score']

    game_data = game_data.merge(teams, left_on='guest', right_on='name') \
        .rename(index=str, columns={'index': 'guest_index'}) \
        .drop('name', axis=1)
    game_data = game_data.merge(teams, left_on='home', right_on='name') \
        .rename(index=str, columns={'index': 'home_index'}) \
        .drop('name', axis=1)

    return game_data


def luck(shots, pm, points):
    # shots (1, 3) --> range(randint(1, 3+1))
    # pm (3, 2) --> [-1]*3 + [1]*2
    # points (1, 5, 2) --> [1]*1 + [2]*5 + [3]*2

    shots_list = range(numpy.random.randint(shots[0], shots[1] + 1))
    pm_list = [-1] * pm[0] + [1] * pm[1]
    points_list = [1] * points[0] + [2] * points[1] + [3] * points[2]

    luck_points = sum([numpy.random.choice(pm_list) * numpy.random.choice(points_list) for i in shots_list])

    return luck_points


def gen_brackets(game_data, teams, n_trials, output_path, shots, pm, points):

    if not os.path.isdir(output_path):
        if os.path.exists(output_path):
            raise ValueError('Output_path exists, but is not a directory.')
        else:
            os.makedirs(output_path)

    n_d1_teams = teams.shape[0]

    # set some constants
    tau = 4.26
    sig = 11
    h   = 4

    # code to compute the probability that one team is better than another based on point spread, x.
    # compute P(Z>0 | X=x) from eq. (12) pnorm(2*tau^2/(sig*sqrt((sig^2+2*tau^2)*(sig^2+4*tau^2)))*x - h/sig*sqrt((sig^2+4*tau^2)/(sig^2+2*tau^2)))
    a = 2*(tau**2)/(sig*numpy.sqrt(((sig**2)+2*(tau**2))*((sig**2)+4*(tau**2))))
    b = 2*(tau**2)*h/(sig*numpy.sqrt(((sig**2)+2*(tau**2))*((sig**2)+4*(tau**2))))

    t = numpy.zeros((n_d1_teams, n_d1_teams, n_trials))

    for trial in range(n_trials):
        start = datetime.datetime.now()
        teams['ngames'] = 0

        for k, row in game_data.iterrows():
            try:
                i = int(row['home_index'])
                j = int(row['guest_index'])

                spread0 = row['spread']

                if not numpy.isnan(spread0):
                    spread = spread0 + luck(shots, pm, points)

                    # Sometimes a gametime is posted before the score is known in the data
                    # This leads to an undefined spread
                    # Skip for now and hope the score is captured in a later update

                    teams.loc[teams['index'] == i, 'ngames'] += 1
                    teams.loc[teams['index'] == j, 'ngames'] += 1

                    r = scipy.stats.norm.cdf(a * spread - b)
                    t[i, j, trial] = t[i, j, trial] + (1.0 - r)
                    t[j, i, trial] = t[j, i, trial] + r
                    t[i, i, trial] = t[i, i, trial] + r
                    t[j, j, trial] = t[j, j, trial] + (1.0 - r)
            except:
                print(i)
                print(j)
                print(spread0)
                print(i, j, spread, row['home'], row['guest'], row['gametime'], r)
                raise

        for i in range(n_d1_teams):
            t[i, :, trial] = t[i, :, trial] / float(teams[teams['index'] == i]['ngames'])

        # initialize ranking procedure
        p = numpy.zeros((1, n_d1_teams))

        z = float(numpy.sum(range(1, n_d1_teams + 1)))
        for i in range(n_d1_teams):
            p[0, i] = (n_d1_teams - i) / z

        # run ranking procedure
        for itr in range(1000):
            p_next = numpy.matmul(p, t[:, :, trial])
            # if(itr % 100 == 0):
            #    print(np.linalg.norm(p_next - p))
            p = p_next

        rank = pandas.DataFrame({'LRMC': p[0], 'team_index': range(n_d1_teams)})
        rank['LRMC_rank'] = rank['LRMC'].rank(ascending=False)
        rank = rank.merge(teams, left_on='team_index', right_on='index', how='left')

        luck_str = '_'.join(map(str, list(itertools.chain.from_iterable((shots, pm, points)))))
        output_file_name = os.path.join(output_path, 'bracket_{}.{}.csv'.format(luck_str, trial))
        rank.sort_values('LRMC_rank').to_csv(output_file_name, index=False)

        print('trial {} of {}'.format(trial, n_trials))
        print('output ranking to: {}'.format(output_path))
        print(rank[(0 < rank['LRMC_rank']) & (rank['LRMC_rank'] <= 4)].sort_values('LRMC_rank'))

        end = datetime.datetime.now()
        print('Trial time in seconds: {}'.format((end - start).total_seconds()))

    return rank


def main(args):
    game_data = read_data(args.data_path)
    teams = get_teams(game_data)

    game_data = add_spread(game_data, teams)

    gen_brackets(game_data, teams, args.n_trials, args.output_path, (0, args.shots), args.pm, args.points)

if __name__ == '__main__':
    main(parse_cl())