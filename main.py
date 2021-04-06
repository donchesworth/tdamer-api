import td_api as td

env_dict = td.tokens.get_envs()
refresh_token = td.tokens.get_refresh_token(env_dict)
access_token = td.tokens.thirty_min_access_token(refresh_token)
positions_df = td.positions.get_full_positions(access_token)
td.positions.add_to_sheet(positions.df)