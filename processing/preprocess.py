from processing.config import raw_data_folder, preprocessed_data_folder, match_config_folder
from processing.process_labels import get_name_and_extension
import os
import json


def rename_data(labeled_data):
    """
    rename players from match_data/match_config/rename_map.json
    player name that do not matched to rename map, are kept as it is
    :param labeled_data:
    :return:
    """
    with open(os.path.join(match_config_folder, 'rename_map.json')) as rename_data:
        rename_map = json.load(rename_data)

    for row in labeled_data:
        if 'match' in row and row['match'] in rename_map:
            renamed_units = []
            if 'units' in row:
                for unit in row['units']:
                    if unit in rename_map[row['match']]:
                        renamed_units.append(rename_map[row['match']][unit])
                    else:
                        renamed_units.append(unit)

            # print(renamed_units)

            row['units'] = renamed_units

    return labeled_data


def covert_to_dict(data_file):
    """
    convert lines of labels to dictionary
    :param data_file:
    :return:
    """
    dict_data = "["
    while True:
        line = data_file.readline()

        if dict_data != '[' and line!= "":
            dict_data += ','

        if line != "":
            dict_data += line
        else:
            break

    dict_data += ']'

    return dict_data


def process_label_format(data_folder, output_folder):
    """
    process the labeled data
    :param data_folder:
    :param output_folder:
    :return:
    """
    for subdir, dirs, files in os.walk(data_folder):
        for filename in files:
            ind = 1
            name_extension = get_name_and_extension(filename)
            name = name_extension['name']
            ext = name_extension['ext'].lower()

            if ext == 'json':
                print(ind, ":", name)

                with open(os.path.join(data_folder, filename), 'r') as data_file:
                    dict_data = covert_to_dict(data_file)

                    json_data = json.loads(dict_data)
                    renamed_data = rename_data(json_data)

                    # print(preprocessed_data)
                    with open(output_folder + name + '.json', 'w') as outfile:
                        json.dump(renamed_data, outfile)
                        outfile.close()

            ind += 1


def preprocess_run_script():
    process_label_format(raw_data_folder, preprocessed_data_folder)


if __name__ == "__main__":
    process_label_format(raw_data_folder, preprocessed_data_folder)