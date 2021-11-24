import pandas as pd
from datetime import datetime
import json
import networkx as nx
import snscrape.modules.twitter as sntwitter

from graphgenerator.src.utils.dataframe_manip import  clean_edges, clean_nodes_RT, clean_nodes_tweet, create_json_output
from graphgenerator.src.utils.tweet_extraction import edge_from_tweet, node_tweet_from_tweet, node_RT_from_tweet
from graphgenerator.src.utils.toolbox import layout_functions
from graphgenerator.config import tz


class GraphBuilder:

    def __init__(self, keyword, type_search, since, algo="spring", minretweets=1, maxresults=None):
        self.keyword = keyword
        self.type_search = type_search
        self.minretweets = minretweets
        self.maxresults = maxresults
        self.since = since
        self.algo = algo
        self.since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=tz)
        self.edges = []
        self.nodes_RT = []
        self.nodes_tweet = []
        self.nodes_tweet_done = []

    def is_valid_tweet(self, tweet):
        """
        Is tweet valid
        """
        return (tweet.retweetedTweet.date > self.since_dt) & (tweet.retweetCount >= self.minretweets)

    def create_search(self):
        """
        Create search string from keyword, type of search and since
        """
        search = f"{self.keyword} {self.type_search}"
        if self.since:
            search += f" since:{self.since}"
        return search

    def collect_tweets(self):
        """
        Collect and save tweets in nodes and edges files
        """
        search = self.create_search()
        print(search)
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
            if self.is_valid_tweet(tweet):
                self.edges.append(edge_from_tweet(tweet))
                self.nodes_RT.append(node_RT_from_tweet(tweet))
                if tweet.retweetedTweet.id not in self.nodes_tweet_done:
                    self.nodes_tweet.append(node_tweet_from_tweet(tweet))
                    self.nodes_tweet_done.append(tweet.retweetedTweet.id)
            if self.maxresults and i > self.maxresults:
                break

    def clean_nodes_edges(self):
        """
        clean node and edges files
        """
        self.edges = clean_edges(self.edges)
        self.nodes_RT = clean_nodes_RT(self.nodes_RT)
        self.nodes_tweet = clean_nodes_tweet(self.nodes_tweet)

        self.nodes = pd.concat([self.nodes_tweet, self.nodes_RT])
        del self.nodes_tweet
        del self.nodes_RT

        self.nodes = self.nodes.sort_values("date", ascending=True)
        self.nodes = self.nodes.groupby(["id", "label", "size"]).agg(
            {col: lambda x: list(x) for col in ["url", "date", "tweet_id", "retweetCount", "role"]}
        ).reset_index()

    def create_graph(self, algo):
        """
        Create graph object using networkx library
        """
        self.G = nx.from_pandas_edgelist(self.edges, source="source", target="target", edge_attr="size")
        position_function = layout_functions[algo]
        self.positions = position_function(self.G)

    def export_json_output(self, output_path):
        """
        Create clean json output
        """
        json_output = create_json_output(self.nodes, self.edges, self.positions)
        with open(output_path, "w") as outfile:
            json.dump(json_output, outfile)


algo = "spring"
NB = GraphBuilder(
    keyword = "#DébatLR",
    minretweets = 10,
    type_search = "filter:nativeretweets",
    since = "2021-11-22",
    maxresults = 2,
)
NB.collect_tweets()
NB.clean_nodes_edges()
NB.create_graph(algo)
NB.export_json_output("test.json")
