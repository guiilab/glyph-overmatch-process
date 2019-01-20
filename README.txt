1. The config.py file contains the information about the file locations.
2. Set the input and output locations (default is already set, but can be changed if necessary).
3. Run the generate_glyph_viz.py script to generate Glyph visualization json file from the labeled data.

Additional Instructions: 
1. There are other three scripts.
-->(a) preprocess.py: this script takes the raw labeled data and converts it to json format 
-->(b) separate_by_match: this script separates the labeled data by match and generates labeled data as json files for all the matches present in the raw labeled data. This labeled data for each match is stored in the "labeled_data" folder
--> (c) process_labels.py: this script handles labeled data file for each match and generate Glyph visualiztion file 
2. generate_glyph_viz.py actually calls these three scripts sequentially to complete the whole process