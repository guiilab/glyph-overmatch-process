# this script takes the raw labeled data from data/Overmatch/raw_data directory and converts that into json format
    # for further processing
# the output is generated in data/Overmatch/preprocessed_data directory


from config import raw_data_folder, preprocessed_data_folder
from process_labels import get_name_and_extension, create_directory
import os
import json


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

                    # print(preprocessed_data)
                    create_directory(output_folder)
                    with open(output_folder + name + '.json', 'w') as outfile:
                        json.dump(json_data, outfile)
                        outfile.close()

            ind += 1


def preprocess_run_script():
    process_label_format(raw_data_folder, preprocessed_data_folder)


if __name__ == "__main__":
    process_label_format(raw_data_folder, preprocessed_data_folder)