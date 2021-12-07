# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:22:29 2021

@author: antoine roy
"""

import click
from datetime import datetime, timedelta

from graphgenerator.version import __version__
from graphgenerator.custom_classes.GraphBuilder import GraphBuilder
from graphgenerator.config import tz


@click.command()
@click.argument("keyword", default="")
@click.option(
    "-r",
    "--minretweets",
    default=1,
    help="The minimal number of retweets a tweet must have for us to fetch its retweeters",
)
@click.option(
    "-d",
    "--since",
    default=(datetime.now(tz=tz) - timedelta(days=7)).strftime("%Y-%m-%d"),
    help="The date up to which we will look for tweets, default is: today's date - 7 days (limit to get the retweets)",
    show_default=True,
)
@click.option(
    "-m",
    "--maxresults",
    default="None",
    help="The maximal number of tweets that we will look at",
    show_default=True,
)
@click.option(
    "-a",
    "--layout_algo",
    default="spring",
    type=click.Choice(["circular", "kamada_kawai", "spring", "random", "spiral"]),
    help="The layout algorithm to use to draw the graph",
    show_default=True,
)
@click.option(
    "-c",
    "--community_algo",
    default="louvain",
    type=click.Choice(
        [
            "greedy_modularity",
            "asyn_lpa_communities",
            "girvan_newman",
            "label_propagation",
            "louvain",
        ]
    ),
    help="The algorithm to use to identify communities in the graph",
    show_default=True,
)
@click.option(
    "-o",
    "--output_path",
    default="output.json",
    help="Path where to export the final Json containing nodes and hedges information",
    show_default=True,
)
@click.option(
    "-g", "--export_graph", is_flag=True, help="Export a jpeg file of the network"
)
@click.option(
    "-j",
    "--graph_path",
    default="graph.png",
    help="Path where to export graph png file",
    show_default=True,
)
@click.option("-v", "--version", is_flag=True, help="Get version of the package")
def main(
    version,
    keyword,
    output_path,
    minretweets,
    since,
    maxresults,
    layout_algo,
    export_graph,
    graph_path,
    community_algo,
):
    """
    Command line utility that export the json of a graph built from a hashtag or expression
    The function is based on the use of the class GraphBuilder:
        - it collects data
        - clean data
        - create the graph object
        - export into json
    """
    if version:
        print(__version__)
    elif keyword == "":
        print("use 'graphgenerator --help' to see how to use the command")
    else:
        start = datetime.now()
        NB = GraphBuilder(
            keyword=keyword, minretweets=minretweets, since=since, maxresults=maxresults
        )
        NB.collect_tweets()
        print("Data collection ended, time of execution is:", datetime.now() - start)
        NB.clean_nodes_edges()
        NB.create_graph(layout_algo)
        print("Graph creation ended, time of execution is:", datetime.now() - start)
        NB.find_communities(community_algo)
        print("Communities algo ended, time of execution is:", datetime.now() - start)
        if export_graph:
            NB.export_img_graph(graph_path)
        NB.export_json_output(output_path)
        end = datetime.now()
        print("The time of execution of the whole program is :", end - start)


if __name__ == "__main__":
    main()
