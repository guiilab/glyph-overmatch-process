# Data Processing for Glyph - Overmatch

### Overview
This package converts a JSON array of labels from the StratMapper database for visualization in Glyph - Overmatch.

Note: users must maintain the file structure in this directory or change filepaths in the config file ('./processing/config.py').

### Get Started
Follow these steps to process the JSON for use in Glyph:

1. Download the repository.
```sh
git clone git@github.com:guiilab/glyph-overmatch-process.git
```
2. Open 'glyph-overmatch-process' in IDE of choice.
<br/>
3. Download labels data from overmatch database. If using a local MongoDB database, export collection using the command line. This will export a JSON array of each label object.
```sh
mongoexport --db overmatch --collection labels --out overmatch_labels.json
```
4. Place this exported data in the raw_data folder (./data/Overmatch/raw_data).
<br/>
5. For each match in the labels data, place the corresponding match config file (formatted for StratMapper visualization) in the match_config folder (./data/Overmatch/match_data/match_config).
<br/>
6. Run generate_glyph_viz.py in IDE of choice or system command line.
<br/>
7.  Check the output folder (./data/Overmatch/output). It will have a JSON file needed for visualization in Glyph. To load this into Glyph, follow the instructions in this [repository](https://github.com/guiilab/glyph-overmatch).