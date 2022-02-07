# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:22:29 2021

@author: antoine roy
"""

import click
from datetime import datetime, timedelta
import json
from dateutil import parser
import dateutil

from graphgenerator.version import __version__
from graphgenerator.custom_classes.GraphBuilder import GraphBuilder
from graphgenerator.config import column_names, tz
from graphgenerator.utils.tweet_extraction import return_last_tweet_snscrape


@click.command()
@click.argument("search", default="")
@click.option(
    "-r",
    "--minretweets",
    default=1,
    help="The minimal number of retweets a tweet must have to fetch its retweeters",
)
@click.option(
    "-f",
    "--input_graph_json_path",
    default=None,
    help="Path to json file containing graph built thanks to graphgenerator command, can be used with option `snscrape_json_path` to enrich it or alone to enrich it with tweets published in the last 7 days",
    show_default=True,
)
@click.option(
    "-s",
    "--snscrape_json_path",
    default=None,
    help="Path to snscrape json output from which to import tweets that will be used to build network, can be used with `input_graph_json_path` to enrich it",
    show_default=True,
)
@click.option(
    "-t",
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
    "-d",
    "--dim",
    default="2",
    type=click.Choice(
        [
            "2",
            "3"        
        ]
    ),
    help="The number of dimension of the layout (can be either 2D or 3D)",
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
@click.option("-b", "--compute_botscore", is_flag=True, help="Compute botscore for each user")
@click.option("-bs", "--batch_size", default=0, help="Size of the batch, if set to 0, the programm uses a single batch")
def main(
    version,
    search,
    json_path,
    snscrape_json_path,
    minretweets,
    since,
    maxresults,
    layout_algo,
    img_path,
    community_algo,
    input_graph_json_path,
    dim,
    compute_botscore,
    batch_size
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
    elif search == "" and input_graph_json_path is None and snscrape_json_path == None:
        print(__version__)
    else:
        start = datetime.now()
        print(start)
        if input_graph_json_path:
            # load json
            with open(input_graph_json_path, "r") as file:
                input_json = json.load(file)
            data_collection_date = parser.parse(
                input_json["metadata"][column_names.metadata_data_collection_date]
            )
            if snscrape_json_path:
                last_tweet = return_last_tweet_snscrape(snscrape_json_path)
                if data_collection_date < parser.parse(last_tweet["date"]):
                    raise Exception("Input graph data is older than data in snscrape json file then it is not possible to use it to update the graph")
            else:
                if data_collection_date + timedelta(days=7) < datetime.now(tz=tz):
                    raise Exception(
                        "Data collection of input graph was performed more than 7 days ago, then it is not "
                        "possible to enrich the graph with new data as data can't be collected before the last"
                        "7 days"
                    )
            # get arguments from input graph
            search = input_json["metadata"][column_names.metadata_search]
            since_id = input_json["metadata"][column_names.metadata_most_recent_tweet]
            minretweets = input_json["metadata"][column_names.metadata_minretweets]
            maxresults = input_json["metadata"][column_names.metadata_maxresults]
            since = input_json["metadata"][column_names.metadata_since]
        elif snscrape_json_path and input_graph_json_path is None:
            search = "unknown as taken from snscrape output"
            since_id = None
            minretweets = 1
            maxresults = None
            since = "2004-01-01"
            input_json = {}
        else:
            input_json = {}
            since_id = None
        if dim=="3" and img_path != "no_img_file":
            raise Exception("graphgenerator can't create a 3D graph in png file. Change dimension to 2D or do not export an image.")
        NB = GraphBuilder(
            search=search,
            minretweets=minretweets,
            since=since,
            maxresults=maxresults,
            since_id=since_id,
            dim=int(dim),
            compute_botscore=compute_botscore
        )
        execution_time = datetime.now()-start
        NB.collect_tweets(
            snscrape_json_path=snscrape_json_path, 
            batch_size=batch_size, 
            input_json=input_json, 
            layout_algo=layout_algo, 
            community_algo=community_algo, 
            img_path=img_path, 
            json_path=json_path, 
            execution_time=execution_time
            )
        print("Data collection ended, time of execution is:", datetime.now() - start)
        NB.clean_nodes_edges(input_json)
        NB.create_graph(layout_algo)
        print("Graph creation ended, time of execution is:", datetime.now() - start)
        NB.find_communities(community_algo)
        print("Communities algo ended, time of execution is:", datetime.now() - start)
        if img_path != "no_img_file":
            NB.export_img_graph(img_path)
        execution_time = datetime.now()-start
        NB.export_json_output(json_path, execution_time)
        print("The time of execution of the whole program is :", execution_time)


if __name__ == "__main__":
    main()
