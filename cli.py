# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:22:29 2021

@author: barre
"""
#!/usr/bin/env python

from retweet_graph import graph_cli
import click
#from botfinder.version import __version__

@click.command()
@click.argument('search')
@click.option('--since')
@click.option('--maxresults')
@click.option('retweets_minimal')

def main(search, since, maxresults, retweets_minimal):
    """Command line utility to estimate the probability of a twitter user to be a bot"""
    print(graph_cli(search, date=since, maxresults=maxresults, retweets_minimal=retweets_minimal))
    
if __name__ == "__main__":
    main()
