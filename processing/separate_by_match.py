# this script takes the preprocessed labeled data from data/Overmatch/preprocessed_data directory and separates
    # labeled data by match
# the output is generated to data/Overmatch/labeled_data directory
# each output file (i.e. 126_ESP.json) is labeled data for the corresponding match

import os
import json
from config import preprocessed_data_folder, labeled_data_folder
from process_labels import get_name_and_extension, create_directory

# list any match that needs to be excluded from processing
exclude_match = []  # for example ['1_ESP', '3_ESP']


def process_file(data):
    """
    process for each match
    :param data:
    :return:
    """
    matches = {}
    for row in data:
        if 'match' in row and row['match'] not in exclude_match:
            if row['match'] not in matches:
                matches[row['match']] = []
                matches[row['match']].append(row)
            else:
                matches[row['match']].append(row)

    return matches


def separate_match_data(data_folder, output_folder):
    """
    separate matches from the labeled data
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
                    data = json.load(data_file)
                    # print(data)
                    labeled_matches = process_file(data)

                    m_c = 1
                    create_directory(output_folder)
                    for match in labeled_matches:
                        print("\t", m_c, ":", match)
                        with open(output_folder + str(match) + '.json', 'w') as outfile:
                            json.dump(labeled_matches[match], outfile)
                            outfile.close()

                        m_c += 1

            ind += 1


def separate_by_match_run_script():
    separate_match_data(preprocessed_data_folder, labeled_data_folder)


if __name__ == "__main__":
    separate_match_data(preprocessed_data_folder, labeled_data_folder)