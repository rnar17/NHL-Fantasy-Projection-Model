# import modules
import numpy as np
import pandas as pd
from random import randint

# import custom functions
from nhl_functions import atoi_to_seconds, normalize_cols, player_comparison_tool

cols_to_round = ['proj_G', 'proj_A', 'proj_+/-', 'proj_PIM', 'proj_PPP', 'proj_ATOI', 'proj_S', 'proj_BLK', 'proj_HIT']

# Store dataframe from excel
stats_df = pd.read_excel(r"C:\Users\naray\Documents\Coding Projects\stats_df.xlsx")
stats_df.drop(columns=[stats_df.columns[0]], inplace=True)

# Create a unique ID for each player
stats_df['Name_Pos'] = stats_df['Player'] + "_" + stats_df['Pos']
unique_name_pos = stats_df['Name_Pos'].unique()
name_pos_id_map = {combo: randint(10000, 99999) for combo in unique_name_pos}
stats_df['ID'] = stats_df['Name_Pos'].map(name_pos_id_map)
id_col = stats_df.pop('ID')
stats_df.insert(0, 'ID', id_col)
stats_df.drop(columns=['Name_Pos'], inplace=True)

# Remove GP outliers
min_gp = 10
stats_df = stats_df[stats_df['GP'] >= min_gp]


# convert ATOI to seconds
stats_df['ATOI'] = stats_df['ATOI'].apply(atoi_to_seconds)

# add normalized stats
df_final = normalize_cols(stats_df)


# Projecting Next Season Stats
current_player_season = '2023-24'
filtered_df = df_final.loc[df_final['Season'] == current_player_season].copy()
filtered_df.loc[:, 'Pts'] = filtered_df['G'] + filtered_df['A']
top_150_ids = filtered_df.sort_values(by='Pts', ascending=False).head(5)['ID'].tolist()
# all_player_ids_2024 = filtered_df['ID'].tolist()

final_projections = []
for player_id in top_150_ids:
    current_player_id = player_id
    projections = player_comparison_tool(current_player_id, current_player_season, df_final)
    if projections is None:
        continue
    final_projections.append(projections)

# put final projections into a dataframe
proj_df = pd.DataFrame(data=final_projections)

# merge dataframes on player_id column and season_ids
df_final_unique = df_final.drop_duplicates(subset='ID', keep='first')
final_df = pd.merge(proj_df, df_final_unique[['ID', 'Player']],  on='ID')

# put player name column in the front
player_col = final_df.pop('Player')
final_df.insert(1, 'Player', player_col)

# round projected values
final_df[cols_to_round] = final_df[cols_to_round].round(0).astype(int)
print(final_df)