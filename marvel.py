from datetime import datetime
import hashlib
import requests
import json
from settings import MARVEL_PUBLIC_KEY, MARVEL_PRIVATE_KEY, MARVEL_URL, METADATA_FILE


class Marvel(object):

    def calculate_md5hash(self, ts):
        """ Calculate the MD5 Hash for the API call
        """
        m = hashlib.md5()
        m.update(ts + MARVEL_PRIVATE_KEY + MARVEL_PUBLIC_KEY)
        return m.hexdigest()

    def construct_querystring(self, offset, limit=100):
        """ Constructs the query string for the URL
        """
        ts = datetime.now().isoformat()
        md5hash = self.calculate_md5hash(ts=ts)
        return '?ts=%s&apikey=%s&hash=%s&limit=%s&offset=%s' % (ts, MARVEL_PUBLIC_KEY, md5hash, limit, offset)

    def get_names(self, limit=100):
        """ A generator that returns the names of characters
            retrieved via the Marvel API.
        """
        offset = 0

        lastname = ''
        while True:
            url = MARVEL_URL + self.construct_querystring(offset=offset)
            print '.'
            try:
                resp = requests.get(url)
            except Exception, e:
                raise Exception('Unable to get data from url %s; error = %s' % (url, e))

            if resp.status_code != 200:
                raise Exception('Error getting Marvel data: status = %s, reason = %s' % (resp.status_code, resp.reason))             

            try:
                json_resp = resp.json()['data']
                results = json_resp['results']
                count = json_resp['count']
            except (KeyError, ValueError), e:
                raise Exception('Unable to process response from url %s; error = %s' % (url, e))

            # Iterate through this batch of results and yield the character name
            # and number of comics with which they are associated
            for i in results:
                if i['name'] != lastname: # avoid duplicates ('Jean Grey' seems to be repeated)
                    lastname = i['name']
                    yield json.dumps({'name': i['name'].encode('utf8').replace('"', ''),
                                      'num_comics': i['comics']['available']})

            if count < limit:
                # We have retrieved all the results, so exit
                break

            offset += limit


def main():
    ''' Call the get_names() generator to read the
        character names, and the number of comics with
        which each is associated, to our metadata file.
    '''

    marvel = Marvel()

    fs = open(METADATA_FILE, 'w')

    for i in marvel.get_names():
        fs.write(i + '\n')
    fs.close()


if __name__ == '__main__':
    main()
