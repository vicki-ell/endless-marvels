#Endless Marvels

##Description

This app reads Marvel character names, then runs a DataSift Stream to obtain relevant social media data. The following summary statistics can subsequently be generated:

 * The characters with the most mentions
 * The character pairs that are mentioned together
 * The characters for which the proportion of mentions is female
 * The most and least liked characters

##Installation
 *  Clone the repo
 *  Install the dependencies (ideally in a virtualenv): 
 ```
 pip install -r dependencies.txt 
 ```
 * Populate the settings.py file with your credentials, The data required is:
  * `MARVEL_PRIVATE_KEY` Your Marvel private API key
  * `MARVEL_PUBLIC_KEY` Your Marvel public API key
  * `DS_USERNAME` Your DataSift username
  * `DS_APIKEY` Your DataSift API Key
  * `METADATA_FILE` The filename in which to save your Marvel metadata
  * `RAW_FILE` The filename in which to save the raw interactions
  * `JSON_FILE` The filename in which to store the summary stats from the raw interactions in JSON format
  

##Running the app

The app can be run with the following command:

```
python stream.py
```
This will get the Marvel metadata (using the Marvel API), then start a DataSift stream based on that metadata. The app must be stopped manually (Ctl C), (not ideal, I know).

Note the optional command line argument:
  
```
usage: stream.py [-h] [--use-existing-metadata]

Firstly, gets metadata from the Marvel API. Then configures and runs a
Datasift Stream based on Marvel characters.

optional arguments:
  -h, --help            show this help message and exit
  --use-existing-metadata
                        If defined, don't contact the Marvel API. Instead,
                        just use the existing contents of the METADATA_FILE
                        defined in settings.py
```



Summary stats can subsequently be generated from the streamed data, by running:
```
python stats.py
```

##App Structure
The app is structured in 3 distinct parts, any of which can be run independently, as long as the dependent files are present:

 * `marvel.py` gets the character names from the Marvel API and stores them in the `METADATA_FILE`
 * `stream.py` constructs and runs a DataSift filter based on the metadata in `METADATA_FILE`. The raw interactions are stored in `RAW_FILE` and relevant data is extracted into `JSON_FILE`
 * `stats.py` processes the JSON data in the `JSON_FILE` and writes some basic stats to stdout.
