import pandas as pd
from datetime import datetime
import json
import networkx as nx
import snscrape.modules.twitter as sntwitter


from utils.dataframe_manip import  clean_edges, clean_nodes_RT, clean_nodes_tweet, create_json_output
from utils.tweet_extraction import edge_from_tweet, node_original, node_RT_quoted, return_type_source_tweet, return_source_tweet
from utils.toolbox import layout_functions
from config import tz


class GraphBuilder:

    def __init__(self, keyword, since, algo="spring", minretweets=1, maxresults=None):
        self.keyword = keyword
        self.minretweets = int(minretweets)
        self.maxresults = None if maxresults == "None" else int(maxresults)
        self.since = since
        self.algo = algo
        self.since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=tz)
        self.type_search = "include:nativeretweets"
        self.edges = []
        self.nodes_RT_quoted = []
        self.nodes_original = []
        self.nodes_original_done = []

    def is_valid_tweet(self, tweet, source_tweet):
        """
        Is tweet valid
        """
        return (source_tweet.date > self.since_dt) & (tweet.retweetCount >= self.minretweets)

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
        n_valid_tweet = 0
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
            is_RT_or_quoted = return_type_source_tweet(tweet)
            if is_RT_or_quoted:
                source_tweet = return_source_tweet(tweet)
                if self.is_valid_tweet(tweet, source_tweet):
                    self.edges.append(edge_from_tweet(tweet, source_tweet))
                    self.nodes_RT_quoted.append(node_RT_quoted(tweet))
                    if source_tweet.id not in self.nodes_original_done:
                        self.nodes_original.append(node_original(tweet, source_tweet))
                        self.nodes_original_done.append(source_tweet.id)
                    n_valid_tweet += 1
                if self.maxresults and n_valid_tweet >= self.maxresults:
                    break

    def clean_nodes_edges(self):
        """
        clean node and edges files
        """
        if self.edges:
            self.edges = clean_edges(self.edges)
            self.nodes_RT_quoted = clean_nodes_RT(self.nodes_RT_quoted)
            self.nodes_original = clean_nodes_tweet(self.nodes_original)

            self.nodes = pd.concat([self.nodes_original, self.nodes_RT_quoted])
            del self.nodes_original
            del self.nodes_RT_quoted

            self.nodes['size'] = self.nodes.groupby(['id', 'label'])['retweetCount'].transform('sum')

            self.nodes = self.nodes.sort_values("date", ascending=True)
            self.nodes = self.nodes.groupby(["id", "label", "size"]).agg(
                {col: lambda x: list(x) for col in ["tweets", "date", "retweetCount", "from"]}
            ).reset_index()
            self.nodes["from"] = self.nodes["from"].apply(lambda x: x[0])
        else:
            raise Exception("No tweet found. Try using other parameters "
                            "(for example decreasing the maximum number of retweets or extending the research window)")

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
