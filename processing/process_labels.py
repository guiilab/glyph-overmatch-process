import os
import json
from processing.config import labeled_data_folder, output_folder, match_config_folder, game

label_fields = ["_id", "event_ids", "units", "events", "id", "title", "author", "timestamp_range", "description",
                "match", "__v"]

PLAYER_TRAJECTORY_MAP = {}

STATE_ID_NAME_MAP = {}
STATES = {}
LINKS = {}
STATE_ID = 0
TRAJECTORIES = {}
TEAM_TRAJECTORIES = {}
TRAJECTORY_ID = 0
TEAM_TRAJECTORY_ID = 0  # change if using the merged trajectory version
TRAJ_SIMILARITY = []
TEAM_TRAJ_SIMILARITY = []

num_players = 0
num_teams = 0

INFINITE_SIMILARITY = 200

similarity_id = 0
team_similarity_id = 0

team_same_traj_count = 0


def get_name_and_extension(file_name):
    """
    get name and extension of a file_name
    :param file_name:
    :return:
    """
    tokens = file_name.split('.')
    return {'name': '.'.join(tokens[0:-1]), 'ext': tokens[-1]}


def create_start_end_states():
    """
    create start and end states/nodes for glyph visualization
    :return:
    """
    global STATE_ID

    if 'Start' not in STATES:
        stateType = 'start'  # start state
        STATES['Start'] = {
            'id': STATE_ID,  # start node has id 0
            'type': stateType,
            'parent_sequence': [],
            'details': {'event_type': 'Start'},
            'stat': {},
            'user_ids': []}

        STATE_ID_NAME_MAP[STATE_ID] = 'Start'
        STATE_ID += 1

    if 'End' not in STATES:
        stateType = 'end'  # end state
        STATES['End'] = {
            'id': 1,  # end node has id 1
            'parent_sequence': [],
            'type': stateType,
            'details': {'event_type': 'End'},
            'stat': {},
            'user_ids': []}

        STATE_ID_NAME_MAP[STATE_ID] = 'End'
        STATE_ID += 1


def create_state(player, label):  # player is a player or a team
    """
    creates state for the given label of a player
    :param player: label of the player
    :param label: given label
    :return:
    """
    global STATE_ID

    state_name = label['title']

    # state already exists??
    if state_name in STATES:
        state = STATES[state_name]
        if player not in state['user_ids']:
            state['user_ids'].append(player)

    # create state
    else:
        state = {
            'id': STATE_ID,
            'parent_sequence': [],
            'type': 'mid',
            'details': {'event_type': state_name},
            'stat': {},
            'user_ids': [player]}

        STATE_ID_NAME_MAP[STATE_ID] = state_name
        STATE_ID += 1
        STATES[state_name] = state

    return state['id']


def link_meaning(source, destination):
    """
    meaning of the transition from state to state
    currently it is set as 'transition' for all
    :param source: source state
    :param destination: destination state
    :return:
    """
    return 'transition'


def add_links(trajectory, user_id):
    """
    adds link between the consecutive nodes of the trajectory
    :param trajectory:
    :param user_id:
    :return:
    """
    action_meaning = []
    for item in range(0, len(trajectory) - 1):
        meaning = link_meaning(trajectory[item], trajectory[item + 1])
        id = str(trajectory[item]) + "_" + str(trajectory[item + 1])  # id: previous node -> current node
        if id not in LINKS:
            LINKS[id] = {'id': id,
                         'source': trajectory[item],
                         'target': trajectory[item + 1],
                         'user_ids': [user_id],
                         'meaning': meaning}

            action_meaning.append(meaning)

        else:
            users = LINKS[id]['user_ids']
            users.append(user_id)
            unique_user_set = list(set(users))
            LINKS[id]['user_ids'] = unique_user_set

            action_meaning.append(LINKS[id]['meaning'])

    return action_meaning


def add_trajectory(player, trajectory, trajectory_key, type, team_data=None):
    """
    add trajectory for the player or the team
    :param player:
    :param trajectory:
    :param trajectory_key:
    :param type: player for player trajectory, team for team trajectory
    :param team_data:
    :return:
    """
    global TRAJECTORY_ID, TRAJECTORIES, TEAM_TRAJECTORIES, TEAM_TRAJECTORY_ID, team_same_traj_count

    if type == 'player':

        if trajectory_key in TRAJECTORIES:
            if player not in TRAJECTORIES[trajectory_key]['user_ids']:
                TRAJECTORIES[trajectory_key]['user_ids'].append(player)
        else:
            user_ids = [player]
            action_meaning = add_links(trajectory, player)

            TRAJECTORIES[trajectory_key] = {'trajectory': trajectory,
                                            'action_meaning': action_meaning,
                                            'user_ids': user_ids,
                                            # 'teams': teams,
                                            'id': TRAJECTORY_ID,
                                            'completed': True}
            TRAJECTORY_ID += 1

        PLAYER_TRAJECTORY_MAP[player] = TRAJECTORIES[trajectory_key]['id']

    elif type == 'team':
        if trajectory_key in TEAM_TRAJECTORIES:
            trajectory_key += ('_c' + str(team_same_traj_count))
            team_same_traj_count += 1
            user_ids = [player]
            action_meaning = add_links(trajectory, player)

            TEAM_TRAJECTORIES[trajectory_key] = {'trajectory': trajectory,
                                                 'action_meaning': action_meaning,
                                                 'user_ids': user_ids,
                                                 # 'teams': teams,
                                                 'id': TEAM_TRAJECTORY_ID,
                                                 'completed': True,
                                                 'team_members': team_data}
            TEAM_TRAJECTORY_ID += 1

            ### if team trajectories are kept together then use the following
            # if player not in TEAM_TRAJECTORIES[trajectory_key]['user_ids']:
            #     TEAM_TRAJECTORIES[trajectory_key]['user_ids'].append(player)

        else:
            user_ids = [player]
            action_meaning = add_links(trajectory, player)

            TEAM_TRAJECTORIES[trajectory_key] = {'trajectory': trajectory,
                                                 'action_meaning': action_meaning,
                                                 'user_ids': user_ids,
                                                 # 'teams': teams,
                                                 'id': TEAM_TRAJECTORY_ID,
                                                 'completed': True,
                                                 'team_members': team_data}
            TEAM_TRAJECTORY_ID += 1


def intersection(lst1, lst2):
    """
    intersection of two lists
    :param lst1:
    :param lst2:
    :return:
    """
    return set(lst1).intersection(lst2)


def label_modification(label_sequence):
    """
    merge lables for overlapping labels and generate a new label
    :param label_sequence:
    :return:
    """
    new_labels = []

    labels = label_sequence['sequence']
    l = len(labels)
    i = 0
    while i < l-1:
        if labels[i+1]['timestamp'][0] < labels[i]['timestamp'][1]:
            print(labels[i]['title'], labels[i]['timestamp'], labels[i]['units'])
            print(labels[i+1]['title'], labels[i+1]['timestamp'], labels[i+1]['units'])

            common = intersection(labels[i]['units'], labels[i+1]['units'])
            print(common)
            print('----------')

            if common:
                merged_title = labels[i]['title'] + '/' + labels[i + 1]['title'] if labels[i]['title'] < labels[i + 1][
                    'title'] else labels[i + 1]['title'] + '/' + labels[i]['title']
            else:
                merged_title = labels[i]['title'] + '-' + labels[i + 1]['title'] if labels[i]['title'] < labels[i + 1][
                    'title'] else labels[i + 1]['title'] + '-' + labels[i]['title']
            merged_units = []
            merged_units.extend(labels[i]['units'])
            merged_units.extend(labels[i+1]['units'])
            label_info = {'events': [], 'event_ids': [], 'title': merged_title,
                          'description': [], 'timestamp': [labels[i]['timestamp'][0], labels[i+1]['timestamp'][1]],
                          'units': merged_units}
            new_labels.append(label_info)
            i += 1
        else:
            print(labels[i]['title'], labels[i]['units'], labels[i]['timestamp'])
            new_labels.append(labels[i])

        i += 1

    return new_labels


def process_single_match_label_data(label_sequence):
    """
    process labeled data for one match
    :param label_sequence: labels sorted by time for player and teams individually
    :return:
    """
    global num_players, num_teams

    for entity in label_sequence:  # item is player or team
        t_data = None
        print('\t' + entity)
        if 'type' in label_sequence[entity] and label_sequence[entity]['type'] == 'player':
            num_players += 1
        elif 'type' in label_sequence[entity] and label_sequence[entity]['type'] == 'team':
            num_teams += 1
            t_data = label_sequence[entity]['team']
        else:
            print(label_sequence)
            print("skip this label: no player or team")

        label_sequence[entity]['sequence'].sort(key=lambda key_id: key_id['timestamp'][0])

        if label_sequence[entity]['type'] == 'team':
            label_sequence[entity]['sequence'] = label_modification(label_sequence[entity])

        STATES['Start']['user_ids'].append(entity)
        STATES['End']['user_ids'].append(entity)

        trajectory_id = "0_"   # trajectory starts with the start state
        trajectory = [0]
        for label in label_sequence[entity]['sequence']:
            state_id = create_state(entity, label)  # create state for the label
            trajectory_id += (str(state_id) + '_')
            trajectory.append(state_id)

        trajectory_id += '1'  # ends with the end state
        trajectory.append(1)

        add_trajectory(entity, trajectory, trajectory_id, label_sequence[entity]['type'], team_data=t_data)


def get_team_players(match_config):
    """
    find out team players from the match information
    :param match_config:
    :return:
    """
    team_info = {}
    units = match_config['units']
    for unit in units:
        if unit['group'] in team_info:
            team_info[unit['group']].append(unit['name'])
        else:
            team_info[unit['group']] = [unit['name']]

    # print(team_info)
    # exit(1)
    return team_info


def process_single_match(match_id, match_data):
    """
    process labels of a single match
    :param match_id:
    :param match_data:
    :return: labels sorted by time for player and teams individually
    """
    with open(os.path.join(match_config_folder, match_id)) as config_data:
        match_config = json.load(config_data)

    team_info = get_team_players(match_config)
    all_units_teams = match_config['units']

    label_sequence = {}

    for row in match_data:
        for unit in row['units']:
            if unit in label_sequence:
                label_info = {'events': row['events'], 'event_ids': row['event_ids'], 'title': row['title'],
                              'description': row['description'], 'timestamp': row['timestamp_range'],
                              'units': row['units']}
                label_sequence[unit]['sequence'].append(label_info)
            else:
                label_sequence[unit] = {'sequence': [], 'type': 'player'}
                label_info = {'events': row['events'], 'event_ids': row['event_ids'], 'title': row['title'],
                              'description': row['description'], 'timestamp': row['timestamp_range'],
                              'units': row['units']}
                label_sequence[unit]['sequence'].append(label_info)

        if len(row['units']) > 1:
            team_list = {}
            for unit in row['units']:
                for unit_team_info in all_units_teams:   # look up which team the unit belongs to
                    if unit_team_info['name'] == unit:
                        if unit_team_info['group'] not in team_list:
                            team_list[unit_team_info['group']] = [unit]
                        else:
                            team_list[unit_team_info['group']].append(unit)
                        break

            for team in team_list:
                if len(team_list[team]) == 1:
                    if team is not None and team not in label_sequence:
                        label_sequence[team] = {'sequence': [], 'type': 'team', 'team': team_info[team]}
                    continue

                if team in label_sequence:
                    label_info = {'events': row['events'], 'event_ids': row['event_ids'], 'title': row['title'],
                                  'description': row['description'], 'timestamp': row['timestamp_range'],
                                  'units': team_list[team]}
                    label_sequence[team]['sequence'].append(label_info)
                else:
                    label_sequence[team] = {'sequence': [], 'type': 'team', 'team': team_info[team]}
                    label_info = {'events': row['events'], 'event_ids': row['event_ids'], 'title': row['title'],
                                  'description': row['description'], 'timestamp': row['timestamp_range'],
                                  'units': team_list[team]}
                    label_sequence[team]['sequence'].append(label_info)

    create_start_end_states()
    process_single_match_label_data(label_sequence)


def is_start_or_end(state):
    """checks is the state is a start or end state"""
    return state['event_type'] == 'start' or state['event_type'] == 'end'


def get_state_diff(state1, state2):
    """
    difference between two states
    :param state1:
    :param state2:
    :return:
    """
    if is_start_or_end(state1) or is_start_or_end(state2):
        if state1 == state2:
            return 0
        else:
            return INFINITE_SIMILARITY

    if state1 == state2:
        return 0
    else:
        return 1


def compute_dtw(traj1, traj2):
    """
    Compute DTW of traj1 and traj2
    States are the important factors
    """
    states1 = traj1
    states2 = traj2

    n = len(states1)
    m = len(states2)
    DTW = []
    for i in range(0, n + 1):
        DTW.append([])
        for j in range(0, m + 1):
            DTW[i].append(INFINITE_SIMILARITY)

    DTW[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = get_state_diff(STATES[STATE_ID_NAME_MAP[states1[i-1]]]['details'],
                                  STATES[STATE_ID_NAME_MAP[states2[j - 1]]]['details'])

            DTW[i][j] = cost + min(DTW[i - 1][j], DTW[i][j - 1], DTW[i - 1][j - 1])

    return DTW[n][m]


def compute_similarity(traj_similarity, traj, team=False):
    """
    compute similarity using DTW for all pairs of trajectories
    :param traj_similarity:
    :param traj:
    :param team:
    :return:
    """
    global similarity_id, team_similarity_id

    json_trajectories = sorted(traj.values(), key=lambda t: t['id'], reverse=False)

    if team and len(json_trajectories) == 0:
        print("No Team in data. Skipping team similarity")
        return

    for i in range(len(json_trajectories) - 1):
        for j in range(i + 1, len(json_trajectories)):
            sim = compute_dtw(json_trajectories[i]['trajectory'],
                              json_trajectories[j]['trajectory'])

            traj_similarity.append({'id': team_similarity_id if team else similarity_id,
                                    'source': json_trajectories[i]['id'],
                                    'target': json_trajectories[j]['id'],
                                    'similarity': sim
                                    })
            if team:
                team_similarity_id += 1
            else:
                similarity_id += 1


def update_team_members_index():
    """
    update team trajectories with the indexes of team members' trajectories
    :return:
    """
    for traj in TEAM_TRAJECTORIES:
        user_index = []
        for user in TEAM_TRAJECTORIES[traj]['team_members']:
            user_index.append(PLAYER_TRAJECTORY_MAP[user])

        TEAM_TRAJECTORIES[traj]['team_members_index'] = user_index


def parse_data_to_json_format():
    """
    generate Glyph json format data
    :return:
    """
    update_team_members_index()

    compute_similarity(TRAJ_SIMILARITY, TRAJECTORIES, team=False)
    print("Individual Similarity Done!")

    compute_similarity(TEAM_TRAJ_SIMILARITY, TEAM_TRAJECTORIES, team=True)
    print("Team Similarity Done!")

    state_list = list(STATES.values())
    link_list = list(LINKS.values())

    trajectory_list = sorted(TRAJECTORIES.values(), key=lambda t: t['id'], reverse=False)
    team_trajectory_list = sorted(TEAM_TRAJECTORIES.values(), key=lambda t: t['id'], reverse=False)

    return {
            'num_users': num_players,
            'num_teams': num_teams,
            'nodes': state_list,
            'links': link_list,
            'team_trajectories': team_trajectory_list,
            'trajectories': trajectory_list,
            'traj_similarity': TRAJ_SIMILARITY,
            'team_traj_similarity': TEAM_TRAJ_SIMILARITY,
            'setting': game + '_label_data'}


def create_directory(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            print("Creation of the directory %s failed" % path)


def process_files(data_folder, output_folder):
    """
    process all the labeled data for different matches
    :param data_folder:
    :param output_folder:
    :return:
    """
    for subdir, dirs, files in os.walk(data_folder):
        ind = 1
        for filename in files:

            name_extension = get_name_and_extension(filename)
            name = name_extension['name']
            ext = name_extension['ext'].lower()

            if ext == 'json':
                print(ind, ":", name)

                with open(os.path.join(data_folder, filename), 'r') as data_file:
                    match_data = json.load(data_file)
                    process_single_match(filename, match_data)

                ind += 1

        break

    output_file_name = game + '_' + str(ind-1) + '_matches'
    json_data = parse_data_to_json_format()

    create_directory(output_folder)
    with open(output_folder + output_file_name + '.json', 'w') as outfile:
        json.dump(json_data, outfile)


def process_labels_run_script():
    process_files(labeled_data_folder, output_folder)


if __name__ == "__main__":
    process_files(labeled_data_folder, output_folder)
