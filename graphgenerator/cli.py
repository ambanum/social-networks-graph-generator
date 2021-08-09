# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:22:29 2021

@author: barre
"""
#!/usr/bin/env python

from graphgenerator.retweet_graph import graph_cli_json, graph_cli_gexf
import click
from graphgenerator.version import __version__

@click.command()
@click.argument('search')
@click.option('--since', help="The date up to which we will look for tweets")
@click.option('--maxresults', help="The maximal number of tweets that we will look at")
@click.option('--retweets_minimal', help="The minimal number of retweets a tweet must have for we to fetch its retweeter")
@click.option('--mode', help="The format returned by the graph either json or gexf. If json it will directly print the result; if gexf it will write a file")
@click.option("-v", "--version", is_flag=True, help="get version of the package")

def main(search, since, maxresults, retweets_minimal, mode='json'):
    """Command line utility that print the json of a graph constructed from a hashtag or expression
    The graph is constructed in the following way :
    We fetch the tweets according to the options
    With these tweets we create nodes for every user who has tweeted something
    And then we add links between two users whenever one user has retweeted another"""
    if version:
        print(__version__)
    if mode=='json' :
        print(graph_cli(search, date=since, maxresults=maxresults, retweets_minimal=retweets_minimal))
    if mode='gexf' :
        graph_cli_gexf(search, date=since, maxresults=maxresults, retweets_minimal=retweets_minimal)
    
if __name__ == "__main__":
    main()

