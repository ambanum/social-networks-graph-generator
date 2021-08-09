# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:22:29 2021

@author: barre
"""
#!/usr/bin/env python

from graphgenerator.retweet_graph import graph_cli
import click

from graphgenerator.version import __version__


@click.command()
@click.argument("search")
@click.option("-d", "--since", help="The date up to which we will look for tweets")
@click.option(
    "-m", "--maxresults", help="The maximal number of tweets that we will look at"
)
@click.option(
    "-r",
    "--retweets_minimal",
    help="The minimal number of retweets a tweet must have for us to fetch its retweeters",
)
@click.option("-v", "--version", is_flag=True, help="get version of the package")
def main(search, since, maxresults, retweets_minimal, version):
    """Command line utility that print the json of a graph constructed from a hashtag or expression
    The graph is constructed in the following way :
    We fetch the tweets according to the options
    With these tweets we create nodes for every user who has tweeted something
    And then we add links between two users whenever one user has retweeted another"""

    if version:
        print(__version__)
    else:
        print(
            graph_cli(
                search,
                since_date="" if since is None else since,
                maxresults="" if maxresults is None else maxresults,
                retweets_minimal=retweets_minimal,
            )
        )


if __name__ == "__main__":
    main()
