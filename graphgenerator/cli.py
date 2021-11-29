# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:22:29 2021

@author: antoine roy
"""

import click

from graphgenerator.version import __version__
from graphgenerator.custom_classes.GraphBuilder import GraphBuilder


@click.command()
@click.argument(
    "keyword",
    default=""
)
@click.option(
    "-r",
    "--minretweets",
    default=1,
    help="The minimal number of retweets a tweet must have for us to fetch its retweeters",
)
@click.option("-d", "--since", default = "2021-11-22", help="The date up to which we will look for tweets")
@click.option(
    "-m", "--maxresults", default = "None", help="The maximal number of tweets that we will look at"
)
@click.option(
    "-a", "--algo", default="spring", help="The layout algorithm you want to use to draw the graph"
)
@click.option(
    "-o", "--output_path", default = "output.json", help="Path where to export the final Json"
)
@click.option("-v", "--version", is_flag=True, help="get version of the package")
@click.option("-g", "--export_graph", is_flag=True, help="export a jpeg file of the network")
@click.option("-j", "--path_graph", default="graph.png", help="path to export graph")
def main(version, keyword, output_path, minretweets, since, maxresults, algo, export_graph, path_graph):
    """
    Command line utility that export the json of a graph built from a hashtag or expression
    """
    if version:
        print(__version__)
    else:
        NB = GraphBuilder(keyword=keyword, minretweets=minretweets, since=since, maxresults=maxresults)
        NB.collect_tweets()
        NB.clean_nodes_edges()
        NB.create_graph(algo)
        if export_graph:
            NB.export_img_graph(path_graph)
        NB.export_json_output(output_path)


if __name__ == "__main__":
    main()
