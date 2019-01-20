game = 'Overmatch'

print("Game: ", game)

# if different player names are wanted. Player names are to be set in match_config/rename_map.json file
preprocessed_data_folder = '../data/' + game + '/preprocessed_data/'

# raw labeled data folder
raw_data_folder = '../data/' + game + '/raw_data/'

# this folder keeps the labeled data separated by match
labeled_data_folder = '../data/' + game + '/labeled_data/'

# this folders keeps information regartion the match: match configuration file from StratMapper
match_data_folder = '../data/' + game + '/match_data/'
match_config_folder = '../data/' + game + '/match_data/match_config/'

# outputs the Glyph visualization json file
output_folder = '../data/' + game + '/output/'

