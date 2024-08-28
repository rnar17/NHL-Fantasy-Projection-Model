import pandas as pd
import xlsxwriter
from random import randint
from time import sleep

seasons = [year for year in range(2008, 2025) if year != 2005]
skater_stats = ['Player', 'Age', 'Pos', 'GP', 'G', 'A', '+/-', 'PIM', 'PPP', 'ATOI', 'S', 'BLK', 'HIT']

# GOAL: append each season's dataframe to the original, parent dataframe

# Initialize an empty DataFrame
stats_df = pd.DataFrame()

for season in seasons:

    # create season stats URL
    stats_url = f"https://www.hockey-reference.com/leagues/NHL_{season}_skaters.html"

    # Read data from website
    stats_dfs = pd.read_html(stats_url)
    temp_df = stats_dfs[0]

    # Initialize temporary DataFrame
    list_of_columns = [col[1] for col in temp_df.columns]
    temp_df.columns = list_of_columns
    first_column = temp_df.columns[0]
    temp_df.set_index(first_column, inplace=True)

    # Rename columns as necessary
    new_column_names = {11: 'G_EV', 12: 'G_PP', 13: 'G_SH', 14:
        'GWG', 15: 'A_EV', 16: 'A_PP', 17: 'A_SH'}
    for col in new_column_names:
        temp_df.columns.values[col] = new_column_names[col]

    # Convert columns to numeric as necessary
    temp_df.drop(columns=['FOW', 'FOL', 'FO%'], errors='ignore', inplace=True)
    indices_to_numeric = [col for col in range(4, 24) if col != 21]
    cols_to_numeric = [temp_df.columns[col] for col in indices_to_numeric]
    for column in cols_to_numeric:
        temp_df[column] = pd.to_numeric(temp_df[column], errors='coerce')

    # Create PPP statistic by adding PP goals to PP assists
    temp_df['PPP'] = temp_df['G_PP'] + temp_df['A_PP']

    # Filter out unneeded columns
    filtered_columns = [col for col in skater_stats if col in temp_df.columns]
    temp_df = temp_df[filtered_columns].copy()  # create a copy to avoid warning message

    # Add season column
    temp_df.insert(0, 'Season', f'{str(season - 1)}-{str(season)[2:]}')

    # Remove duplicate player ID's
    duplicates = temp_df.index.duplicated(keep='first')
    temp_df = temp_df.loc[~duplicates]

    # Get rid of repeated column headers
    temp_df.dropna(axis=0, how='any', inplace=True)

    # Concatenate temp_df to the end of stats_df
    stats_df = pd.concat([stats_df, temp_df], ignore_index=True)

    # delay next iteration
    sleep(randint(10, 25))

# Export dataframe to excel for future use
stats_df.to_excel(r"C:\Users\naray\Documents\Coding Projects\NHL Projection Model\stats_df.xlsx", engine='xlsxwriter')