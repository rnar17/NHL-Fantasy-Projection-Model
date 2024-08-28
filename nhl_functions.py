# Custom functions used for Projection model

# import modules
import numpy as np
import pandas as pd

season_list = [f'{str(x)}-{str(x + 1)[2:]}' for x in range(2007, 2025)]
cols_to_norm = scoring_stats = ['G', 'A', '+/-', 'PIM', 'PPP', 'ATOI', 'S', 'BLK', 'HIT']


def atoi_to_seconds(col):
    minutes, seconds = map(int, col.split(':'))
    return minutes * 60 + seconds


def normalize(col):
    return (col - col.min()) / (col.max() - col.min())  # normalization formula


def normalize_cols(df):
    for col_name in cols_to_norm:
        df[f'{col_name}_norm'] = normalize(df[col_name])
    return df


# function to calculate distance between two points
def calc_distance(p1, p2):
    dist_vec = p1 - p2
    dist = np.sqrt(np.sum(dist_vec ** 2))
    return dist


# function to find the DataFrame row of a player given id and season
def find_player(player_id, season, df):
    for index, row in df.iterrows():
        if season == row['Season'] and player_id == row['ID']:
            return row


# function to find the normalized stats of a player given id and season
def current_player_stats(current_player_id, current_player_season, df):
    return np.array([
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'G_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'A_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), '+/-_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'PIM_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'PPP_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'ATOI_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'S_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'BLK_norm']).item(),
        (df.loc[(df['ID'] == current_player_id) & (df['Season'] == current_player_season), 'HIT_norm']).item()
    ])


# function to find the next year projected stats of a player
def player_comparison_tool(current_player_id, current_player_season, df):

    if not ((df['Season'] == current_player_season) & (df['ID'] == current_player_id)).any():
        print(f"Can't find player with id {current_player_id} and season {current_player_season}")
        return None

    for row in df.itertuples():
        if current_player_season == row.Season and current_player_id == row.ID:
            break

    current_player_vector = current_player_stats(current_player_id, current_player_season, df)
    print(
        f"Projecting player_id {current_player_id} for season {season_list[season_list.index(current_player_season) + 1]}")

    player_distance = []

    weighted_numbers = [1, 1, 1, 1, 1, 1, 1, 1, 1]

    for index, row in df.iterrows():
        compared_player_vector = np.array([
            row['G_norm'],
            row['A_norm'],
            row['+/-_norm'],
            row['PIM_norm'],
            row['PPP_norm'],
            row['ATOI_norm'],
            row['S_norm'],
            row['BLK_norm'],
            row['HIT_norm']
        ])

        vfunc = np.vectorize(calc_distance)
        distance_vec = vfunc(current_player_vector, compared_player_vector)
        weighted_distance = distance_vec * weighted_numbers
        number = np.sum(np.abs(weighted_distance)) / len(
            distance_vec)  # standardized singular number that compares players
        player_distance.append(number)

    df['distance'] = player_distance
    ranked_df = df.sort_values('distance')
    print(ranked_df.iloc[1:11])
    projected_stats = {}
    for col in scoring_stats:
        sum_stat = 0
        sum_weight = 0
        for index, row in ranked_df.iloc[1:11].iterrows():
            # skip over row if it is the 2023-24 season because we can't take the next season
            if row['Season'] == '2023-24':
                continue
            weight = 1 / row.distance
            next_season = season_list[season_list.index(row['Season']) + 1]
            # return row of player next season stats
            player_next_season = find_player(row['ID'], next_season, df)
            # If player next season is not found (retire or otherwise) then skip
            if player_next_season is None:
                continue
            sum_stat += player_next_season[col] * weight
            sum_weight += weight
        projected_stats['ID'] = current_player_id
        projected_stats['proj_season'] = season_list[season_list.index(current_player_season) + 1]
        projected_stats[f'proj_{col}'] = sum_stat / sum_weight

    return projected_stats
