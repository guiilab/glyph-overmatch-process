# this script runs three scripts
# 1. preprocess.py: preprocesses the labeled data
# 2. separate_by_match.py: separates labeled data by match and generates labeled data for each match
# 3. process_labels.py: processes labeled data of each match and generates Glyph visualization file

from processing.preprocess import preprocess_run_script
from processing.separate_by_match import separate_by_match_run_script
from processing.process_labels import process_labels_run_script


if __name__ == "__main__":
    print("----------------- Preprocessing labeled data ...")
    preprocess_run_script()

    print("----------------- Separating labeled data by match ...")
    separate_by_match_run_script()

    print("----------------- Processing labels and generating Glyph Visualization ...")
    process_labels_run_script()