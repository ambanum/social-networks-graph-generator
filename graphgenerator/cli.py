# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:22:29 2021

@author: antoine roy
"""

import click
from datetime import datetime, timedelta
import json
from dateutil import parser

from graphgenerator.version import __version__
from graphgenerator.custom_classes.GraphBuilder import GraphBuilder
from graphgenerator.config import column_names, tz


@click.command()
@click.argument("search", default="")
@click.option(
    "-r",
    "--minretweets",
    default=1,
    help="The minimal number of retweets a tweet must have for us to fetch its retweeters",
)
@click.option(
    "-f",
    "--input_graph_json_path",
    default="no_input_graph",
    help="Path to json file containing graph built thanks to graphgenerator command",
    show_default=True,
)
@click.option(
    "-d",
    "--since",
    default="2004-01-01",
    help="The date up to which we will look for tweets, the graphgenerator can only get last 7 days Retweets",
    show_default=True,
)
@click.option(
    "-m",
    "--maxresults",
    default="None",
    help="The maximal number of tweets that will be retrieved",
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
    help="The algorithm used to identify communities in the graph",
    show_default=True,
)
@click.option(
    "-j",
    "--json_path",
    default="output.json",
    help="Path where to export the final Json containing nodes and hedges information",
    show_default=True,
)
@click.option(
    "-i",
    "--img_path",
    default="no_img_file",
    help="Path where to export graph png file, if not specified then no graph is exported",
    show_default=True,
)
@click.option("-v", "--version", is_flag=True, help="Get version of the package")
def main(
    version,
    search,
    json_path,
    minretweets,
    since,
    maxresults,
    layout_algo,
    img_path,
    community_algo,
    input_graph_json_path,
):
    """
    Command line utility that export the json of a graph built from a hashtag or expression
    The function is based on the use of the class GraphBuilder:
        - it collects data and loads existing data if specified
        - clean data
        - create the graph object
        - export into json
    """
    if version:
        print(__version__)
    elif search == "" and input_graph_json_path == "no_input_graph":
        print(__version__)
    else:
        start = datetime.now()
        print(start)
        if input_graph_json_path != "no_input_graph":
            #load json
            with open(input_graph_json_path, "r") as file:
                input_json = json.load(file)
            data_collection_date = parser.parse(input_json["metadata"][column_names.metadata_data_collection_date])
            if data_collection_date + timedelta(days=7) < datetime.now(tz=tz):
                raise Exception("Data collection of input graph was performed more than 7 days ago, then it is not "
                                "possible to enrich the graph with new data as data can't be collected before the last"
                                "7 days")
            # get arguments from input graph
            search = input_json["metadata"][column_names.metadata_search] + " since_id:%s" % input_json["metadata"][
                column_names.metadata_most_recent_tweet]
            minretweets = input_json["metadata"][column_names.metadata_minretweets]
            since = input_json["metadata"][column_names.metadata_since]
        else:
            input_json = {}
        NB = GraphBuilder(
            search=search, minretweets=minretweets, since=since, maxresults=maxresults
        )
        NB.collect_tweets()
        print("Data collection ended, time of execution is:", datetime.now() - start)
        NB.clean_nodes_edges(input_json)
        NB.create_graph(layout_algo)
        print("Graph creation ended, time of execution is:", datetime.now() - start)
        NB.find_communities(community_algo)
        print("Communities algo ended, time of execution is:", datetime.now() - start)
        if img_path != "no_img_file":
            NB.export_img_graph(img_path)
        NB.export_json_output(json_path)
        end = datetime.now()
        print("The time of execution of the whole program is :", end - start)


if __name__ == "__main__":
    main()
