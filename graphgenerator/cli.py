# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:22:29 2021

@author: antoine roy
"""
#!/usr/bin/env python

import click

from version import __version__
from custom_classes.GraphBuilder import GraphBuilder


@click.command()
@click.argument(
    "keyword"
)
@click.option(
    "-r",
    "--minretweets",
    help="The minimal number of retweets a tweet must have for us to fetch its retweeters",
)
@click.option("-d", "--since", help="The date up to which we will look for tweets")
@click.option(
    "-m", "--maxresults", help="The maximal number of tweets that we will look at"
)
@click.option(
    "-a", "--algo", help="The layout algorithm you want to use to draw the graph"
)
@click.option(
    "-o", "--output_path", help="Path where to export the final Json"
)

#@click.option(
#    "-vvv",
#    "--verbose",-v
#    help="display debug logs. CAUTION: can't be used with jq as result will not be only valid json",
#    is_flag=True,
#)
@click.option("-v", "--version", is_flag=True, help="get version of the package")
def main(version, keyword, output_path, minretweets=10, since="2021-11-22", maxresults=None, algo="spring"):
    """
    Command line utility that export the json of a graph constructed from a hashtag or expression
    """
    if version:
        print(__version__)
    else:
        NB = GraphBuilder(
            keyword=keyword,
            minretweets=minretweets,
            since=since,
            maxresults=maxresults,
        )
        NB.collect_tweets()
        NB.clean_nodes_edges()
        NB.create_graph(algo)
        NB.export_json_output(output_path)


if __name__ == "__main__":
    main()
