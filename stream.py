import datasift
import json
import argparse
from datetime import datetime, timedelta
from marvel import Marvel
from datasift.exceptions import DataSiftApiException
from settings import DS_USERNAME, DS_APIKEY, METADATA_FILE, RAW_FILE, JSON_FILE


def build_json(msg):
    ''' Extracts relevant data from the raw interaction
        and adds it to the JSON structure
    '''
    fs = open('data/%s' % JSON_FILE, 'r+')

    try:
        stats = json.load(fs)
    except ValueError:
        stats = {}

    try:
        tags = msg['interaction']['tags']
    except KeyError:
        tags = []

    try:
        gender = msg['demographic']['gender']
    except KeyError:
        gender = None
    
    sentiment = 0
    try:
        for k in msg['salience'].keys():
            sentiment += msg['salience'][k]['sentiment']
    except KeyError:
        sentiment = 0


    for name in tags:
        # If this is the first instance of this
        # character then setup the empty dict
        if name not in stats:
            stats[name] = {"mentions": 0,
                           "female": 0,
                           "sentiment": 0,
                           "associated": {}}

        # increment the number of mentions
        stats[name]['mentions'] += 1

        # increment if this is a female user
        if gender in ['female', 'mostly_female']:
            stats[name]['female'] += 1

        # adjust the sentiment
        stats[name]['sentiment'] += sentiment
        
        # increment the characters that were also
        # tagged in this interaction
        associated = [t for t in tags if t != name]

        for i in associated:
            if i not in stats[name]['associated'].keys():
                stats[name]['associated'][i] = 1
            else:
                stats[name]['associated'][i] += 1

    # Write the new JSON struct to the file
    fs.seek(0)
    json.dump(stats, fs)
    fs.truncate()
    fs.close()


def construct_filter(metadata_file):
    ''' Firstly, reads the metadata from the input file, and from that
        takes the top 500 characters, based on the number of comics with
        which they are associated.

        A DataSift query is then constructed based on those characters.
        The filter checks for any of those 'top 500' characters, and tags
        them for future use.
    '''

    # Get the top 500 characters
    fs = open(metadata_file, 'r')
    all_data = [json.loads(i) for i in fs.readlines()]
    fs.close()
    top500 = sorted(all_data, key=lambda k: k['num_comics'], reverse=True)[:500]

    # Build the query string and tags for the filter
    qstr = ''
    tags = ''
    for i in top500:
        tags += 'tag "%s" { interaction.content contains "%s" }\n' % (i['name'], i['name'])
        if qstr:
            qstr += ','
        qstr += i['name']

    # Construct the filter
    csdl = '''%s\n

    return
    {
        interaction.content contains_any "%s" and (interaction.content contains "Marvel" or interaction.title contains "Marvel")
    }
    ''' % (tags, qstr)

    return csdl


def get_marvel_names():
    ''' Call the get_names() generator to read the
        character names and the number of comics with
        which each is associated. Writes the results to
        the metadata file.
    '''

    marvel = Marvel()

    fs = open('data/%s' % METADATA_FILE, 'w')

    for i in marvel.get_names():
        fs.write(i + '\n')
    fs.close()


def main():
    ''' Firstly, gets the metadata from the Marvel API.

        Then creates the Datasift client, constructs the filter and starts
        consuming data.

        Data is saved to 2 files:
        1) The raw interactions are saved to a file.
        2) Relevant data is extracted from the raw interactions saved in JSON format.
    '''
    parser = argparse.ArgumentParser(description='''Firstly, gets metadata from the Marvel API. 
                                                 Then configures and runs a Datasift Stream based on Marvel characters.''')
    parser.add_argument('--use-existing-metadata', action='store_true', 
                                                   help='''If defined, don't contact the Marvel API. Instead, just use the
                                                   existing contents of the METADATA_FILE defined in settings.py''')
    args = vars(parser.parse_args())

    # Get the metadata from the Marvel API, if required.
    if not args['use_existing_metadata']:
        print 'Getting marvel names....'
        get_marvel_names()

    # Authenticate the client
    client = datasift.Client(DS_USERNAME, DS_APIKEY)

    # Construct the filter
    csdl = construct_filter('data/%s' % METADATA_FILE)

    try:
        hash = client.compile(csdl)["hash"]
    except DataSiftApiException, e:
        print "Error compiling the DS filter: %s" % e

    # Tell me the cost
    print "This stream will use %s dpus" % client.dpu(hash)['dpu']

    @client.on_delete
    def on_delete(interaction):
        print "You must delete this to be compliant with T&Cs: ", interaction

    @client.on_closed
    def on_close(wasClean, code, reason):
        print "Stream subscriber shutting down because ", reason

    @client.on_ds_message
    def on_ds_message(msg):
        print('DS Message %s' % msg)

    @client.on_open
    def on_open():

        # Empty the files
        fs_raw = open('data/%s' % RAW_FILE, 'w').close()
        fs_json = open('data/%s' % JSON_FILE, 'w').close()
        
        @client.subscribe(hash)
        def on_interaction(interaction):
            print '.'
     
            # Store the raw interaction
            fs_raw = open('data/%s' % RAW_FILE, 'a')
            fs_raw.write('%s\n' % interaction)
            fs_raw.close()
          
            # Extract some useful stats in JSON format
            build_json(interaction)

    # Start consuming data
    print 'Starting the Datasift Stream. Press Ctl C to exit......'
    client.start_stream_subscriber()


if __name__ == '__main__':
    main()

