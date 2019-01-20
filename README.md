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
3. Download labels data from overmatch database. If using a local MongoDB database, export collection using the command line:
```sh
mongoexport --db overmatch --collection labels --out overmatch_labels.json
```
This will export a JSON array of each label object.
<br/>

4. 


4. Place CSV files in replays folder ('./data/replays'). By default, there are two files (126_ESP.csv, 221_ESP.csv) in this folder for demonstration purposes. To process different files, remove these.
<br/>
4. Run 'raw_to_stratmapper.py' file in IDE or shell of choice.
<br/>
5. Check output folder ('./data/output'). There will be JSON files for each CSV file, as well as a directory 'config' with a 'matches_config.json' file, which is a JSON Array of formatted match files (one for each csv file in replays folder).
<br/>
6. To load these files into StratMapper, follow the instructions in this [repository](https://github.com/guiilab/stratmapper-overmatch).