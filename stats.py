from settings import JSON_FILE
import json


class StatsPrinter(object):
    ''' Generates and prints stats on saved Datasift data
    '''
    def __init__(self):

        fs = open('data/%s' % JSON_FILE, 'r')
        self.data = json.load(fs)
        fs.close()

       # fs = open('data/%s' % JSON_FILE, 'r')
       # self.data = json.loads(fs.read())
       # fs.close()


    def print_stats(self, data, key=None, max=10):
        ''' Prints a list of stats.

            Enumerate through a list of tuples, where the first
            value in the tuple is the label to be displayed (character
            or character pair), and the second value in the tuple is
            the associated count, (may be a dict, in which case the key
            is supplied).

            Ties (where, for example, more than one character has the same count)
            are detected and displayed accordingly.
        '''

        last_count = -1
        for index, value in enumerate(data):
            try:
                count = value[1][key]
            except TypeError:
                count = value[1]
 
            if not count:
                # If we've reached zero then don't display anymore entries
                break

            if last_count != count:
                if index+1 > max:
                    break

                print '%s: %s: %s' % (index+1, value[0], count)
                last_count = count
                last_index = index
            else:
                # This value is tied with the previous value
                print '%s=: %s: %s' % (last_index+1, value[0], count)

        print '\n'


    def print_mention_stats(self):
        ''' Calculates and displays the top 10 characters
            based on the number of mentions.
        '''
        top_mentions = sorted(self.data.items(), key=lambda k: k[1]['mentions'], reverse=True)
        print '========================================================'
        print 'The top characters by number of mentions are:'
        self.print_stats(top_mentions, 'mentions')


    def print_gender_stats(self):
        ''' Calculates and displays the characters which
            have the most female mentioners
        '''
        top_females = sorted(self.data.items(), key=lambda k: k[1]['female'], reverse=True)
        print '========================================================'
        print 'The top characters by female users are:'
        self.print_stats(top_females, 'female')


    def print_sentiment_stats(self):
        ''' Calculates and displays the most liked
            and disliked characters
        '''
        most_liked = sorted(self.data.items(), key=lambda k: k[1]['sentiment'], reverse=True)
        print '========================================================'
        print 'The most liked characters (with a sentiment > 0) are:'
        self.print_stats(most_liked, 'sentiment')

        most_disliked = sorted(self.data.items(), key=lambda k: k[1]['sentiment'])
        print '========================================================'
        print 'The least like characters (with a sentiment < 0) are:'
        self.print_stats(most_disliked, 'sentiment')


    def print_association_stats(self):
        ''' Calculates and displays the top character pairs
            based on the number of times two characters are mentioned
            in the same interaction.
        '''
        associations = []
        for k, v in self.data.iteritems():
            for name, count in v['associated'].iteritems():
                if ('%s and %s' % (name, k), count) not in associations:
                    associations.append(('%s and %s' % (k, name), count))

        top_associations = sorted(associations, key=lambda k: k[1], reverse=True)
        print '\n========================================================'
        print 'The top 10 most commonly associated character pairs are:'
        self.print_stats(top_associations)


def main():

    stats = StatsPrinter()

    stats.print_mention_stats()
    stats.print_association_stats()
    stats.print_gender_stats()
    stats.print_sentiment_stats()


if __name__ == '__main__':
    main()
