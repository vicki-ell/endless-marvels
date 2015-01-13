import plotly.plotly as py
from plotly.graph_objs import *
import json
import argparse


def most_mentions(data):
    ''' Bar chart displaying the characters with the most mentions,
        broken down by male/female users.
    '''
    sorteddata = sorted(data.items(), key=lambda x : x[1]['mentions'], reverse=True)

    xdata = [x[0] for x in sorteddata]
    ydata = [x[1]['mentions'] - x[1]['female'] for x in sorteddata]
    ydatafemale = [x[1]['female'] for x in sorteddata]

    trace1 = Bar(
        x=xdata,
        y=ydata,
        name='Male'
    )
    trace2 = Bar(
        x=xdata,
        y=ydatafemale,
        name='Female'
    )
    data = Data([trace1, trace2])
    layout = Layout(
        barmode='stack',
        title='Number of Mentions for Each Character'
    )

    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='stacked-bar')


def most_popular(data):
    ''' Bar chart displaying the most popular characters
    '''
    sorteddata = sorted(data.items(), key=lambda x : x[1]['sentiment'], reverse=True)

    xdata = [x[0] for x in sorteddata]
    ydata = [x[1]['sentiment'] for x in sorteddata]

    colors = []
    for i in ydata:
        if i > 0:
            colors.append('#447adb')
        else:
            colors.append('#db5a44')

    data = Data([
        Bar(
            x=xdata,
            y=ydata,
            marker=Marker(
                color=colors
            )
        )
    ])


    layout = Layout(
        title='Popularity of Each Character'
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='basic-bar')


def mentions_vs_popular(data):
    ''' Scatterplot displaying the number of mentions vs
        the popularity of the character.
    '''

    datalist = data.items()
    xdata = [x[1]['mentions'] for x in datalist]
    ydata = [x[1]['sentiment'] for x in datalist]

    names = [x[0] for x in datalist]

    trace1 = Scatter(
        x=xdata,
        y=ydata,
        mode='markers',
        text=names,
        marker=Marker(
        color='rgb(164, 194, 244)',
        size=12,
        line=Line(
            color='white',
            width=0.5
            )
        )
    )

    data = Data([trace1])
    layout = Layout(
        title='Number of mentions vs Popularity',
        xaxis=XAxis(
            title='Number of Mentions',
            showgrid=False,
            zeroline=False
        ),
        yaxis=YAxis(
            title='Popularity',
            showline=False
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='line-style')



def most_influential(data):
    ''' Bar chart displaying the top 20 most prolific users
    '''
    sorteddata = sorted(data.items(), key=lambda x : x[1]['reblogged'], reverse=True)[:20]

    xdata = [x[0] for x in sorteddata]
    ydata = [x[1]['reblogged'] for x in sorteddata]

    data = Data([
        Bar(
            x=xdata,
            y=ydata
        )
    ])

    layout = Layout(
        title='Most Influential Usernames on Tumblr'
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='basic-bar')

def reblogged_vs_likes(data):
    ''' Scatter chart plotting the number of reblogged posts 
        vs the number of likes for each user
    '''

    datalist = data.items()

    xdata = [x[1]['reblogged'] for x in datalist]
    ydata = [x[1]['likes'] for x in datalist]
    names = [x[0] for x in datalist]

    trace1 = Scatter(
        x=xdata,
        y=ydata,
        mode='markers',
        text=names,
        marker=Marker(
            color='rgb(164, 194, 244)',
            size=12,
            line=Line(
                color='white',
                width=0.5
            )
        )
    )

    data = Data([trace1])
    layout = Layout(
        title='Number of Tumblr Reblogs vs Number of Likes',
        xaxis=XAxis(
            title='Number of Reblogs',
            showgrid=False,
            zeroline=False
        ),
        yaxis=YAxis(
            title='NUmber of Likes',
            showline=False
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='line-style')


def main():

    parser = argparse.ArgumentParser(description='''Displays graphs from the Marvel data''')
  
    parser.add_argument('graph', metavar='G', type=str, help='the graph type, ("mentions", "popular", "mentionsvspopular", "influential", "rebloggedvslikes")')
    args = vars(parser.parse_args())

    fs = open('data.json', 'r')
    data = json.load(fs)
    fs.close()

    fs = open('usernames.json', 'r')
    usernames = json.load(fs)
    fs.close()

    if args['graph'] == 'mentions':
        most_mentions(data)
    elif args['graph'] == 'popular':
        most_popular(data)
    elif args['graph'] == 'mentionsvspopular':
        mentions_vs_popular(data)
    elif args['graph'] == 'influential':
        most_influential(usernames)
    elif args['graph'] == 'rebloggedvslikes':
        reblogged_vs_likes(usernames)
    else:
        print 'Invalid graph type. Please pick one of : "mentions", "popular", "mentionsvspopular", "influential", "rebloggedvslikes"'


if __name__=='__main__':
    main()
