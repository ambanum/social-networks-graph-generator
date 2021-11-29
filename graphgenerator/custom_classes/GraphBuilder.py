from datetime import datetime
import json
import networkx as nx
import snscrape.modules.twitter as sntwitter
import matplotlib.pyplot as plt


from graphgenerator.utils.dataframe_manip import clean_edges, concat_clean_nodes, create_json_output
from graphgenerator.utils.tweet_extraction import edge_from_tweet, node_original, node_RT_quoted, return_type_source_tweet, return_source_tweet
from graphgenerator.utils.toolbox import layout_functions
from graphgenerator.config import tz


class GraphBuilder:
    """
    Download all tweets mentioning a specific topic since a specific date and build network of retweets and quotes of
    accounts mentioning this topic
    """
    type_search = "include:nativeretweets"
    edges = []
    nodes_original_done = []
    nodes = []
    G = []
    positions = []
    last_collected_tweet = ""
    last_collected_date = ""

    def __init__(self, keyword, since, minretweets=1, maxresults=None):
        self.keyword = keyword
        self.minretweets = int(minretweets)
        self.maxresults = None if (maxresults == "None") or (maxresults is None) else int(maxresults)
        self.since = since
        self.since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=tz)
        self.nodes_original = []
        self.nodes_RT_quoted = []

    def is_valid_tweet(self, tweet, source_tweet):
        """
        Is tweet valid i.e. :
        - the source tweet was published after the specified date in since
        - the number of retweet to consider is above the number of retweets specified in Class
        - the user is not retweeting or mentionning him/herself
        """
        return (source_tweet.date > self.since_dt) & (tweet.retweetCount >= self.minretweets) & (tweet.username != source_tweet.username)

    def create_search(self):
        """
        Create search string from keyword, type of search and since date
        """
        search = f"{self.keyword} {self.type_search}"
        if self.since:
            search += f" since:{self.since}"
        return search

    def collect_tweets(self):
        """
        Collect and save tweets in nodes and edges files, for each tweet, the source tweet is also collected
        data collection ist stopped when their ist no more tweet or if the maximum number of tweets to collect is reached
        (the number of tweet = number of retweets + number of quotes,)
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
                    self.nodes_RT_quoted.append(node_RT_quoted(tweet, source_tweet))
                    if source_tweet.id not in self.nodes_original_done:
                        self.nodes_original.append(node_original(tweet, source_tweet))
                        self.nodes_original_done.append(source_tweet.id)
                    n_valid_tweet += 1
                self.last_collected_tweet = tweet.id
                self.last_collected_date = tweet.date
                if self.maxresults and n_valid_tweet >= self.maxresults:
                    break

    def clean_nodes_edges(self):
        """
        clean node and edges files and delete old files that are not usefull anymore
        """
        if self.edges:
            self.edges = clean_edges(self.edges, self.last_collected_date)
            self.nodes = concat_clean_nodes(self.nodes_RT_quoted, self.nodes_original, self.last_collected_date)
            del self.nodes_original
            del self.nodes_RT_quoted
        else:
            raise Exception("No tweet found. Try using other parameters "
                            "(for example decreasing the maximum number of retweets or extending the research window)")

    def create_graph(self, algo="spring"):
        """
        Create graph object using networkx library and calculate positions of nodes using algo
        """
        self.G = nx.from_pandas_edgelist(self.edges, source="source", target="target", edge_attr="size")
        position_function = layout_functions[algo]["function"]
        self.positions = position_function(self.G, **layout_functions[algo]["args"])

    def export_img_graph(self, path_graph="Graph.png"):
        """
        Export an image of the network
        """
        plt.figure(figsize=(30, 30))
        nx.draw_networkx(
            self.G, pos=self.positions, arrows=True, with_labels=False, font_size=15, node_size=10, alpha=0.5
        )
        plt.savefig(path_graph, format="PNG")

    def export_json_output(self, output_path="output.json"):
        """
        Create clean json output
        """
        json_output = create_json_output(self.nodes, self.edges, self.positions)
        json_output["metadata"] = {
            "keyword": self.keyword,
            "since": self.since,
            "type_search": self.type_search,
            "maxresults": self.maxresults,
            "minretweets": self.minretweets,
            "last_collected_tweet": self.last_collected_tweet
        }
        with open(output_path, "w") as outfile:
            json.dump(json_output, outfile)
