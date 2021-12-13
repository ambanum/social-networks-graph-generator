from datetime import datetime, timedelta
import json
import networkx as nx
import snscrape.modules.twitter as sntwitter
import matplotlib.pyplot as plt


from graphgenerator.utils.dataframe_manip import (
    clean_edges,
    concat_clean_nodes,
    create_json_output,
)
from graphgenerator.utils.tweet_extraction import (
    edge_from_tweet,
    node_original,
    node_RT_quoted,
    return_type_source_tweet,
    return_source_tweet,
)
from graphgenerator.utils.toolbox import layout_functions, community_functions
from graphgenerator.config import tz, column_names


class GraphBuilder:
    """
    Class to build a graph from a search of a keyword or hashtag on twitter
    Download all tweets mentioning a specific topic since a specific date and build network of retweets and quotes of
    accounts mentioning this topic
    """

    def __init__(self, search, since, minretweets=1, maxresults=None):
        """
        Init function of class GraphBuilder
            Parameters:
                search (str): search you want to perform on Twitter (string that would type in twitter search bar)
                since (str): date in format %Y-%m-%d from where to start search, it must fall in the 7 last days
                otherwise it will be changed to the date 7 days ago (we can't get retweets from more than 7 days ago)
                minretweets (int): minimal number of retweets a tweet should have to be collected
                maxresults (int): maximum number of RT and quotes to include in the graph
        """
        self.search = search
        self.minretweets = int(minretweets)
        self.maxresults = (
            None if (maxresults == "None") or (maxresults is None) else int(maxresults)
        )
        self.since = since
        self.get_valid_date()
        self.nodes_original = []
        self.nodes_RT_quoted = []
        self.nodes_original_done = []
        self.type_search = "include:nativeretweets"
        self.edges = []
        self.nodes = []
        self.G = []
        self.positions = []
        self.communities = {}
        self.last_collected_tweet = ""
        self.most_recent_tweet = ""
        self.data_collection_date = ""
        self.last_collected_date = ""
        self.data_collected = False
        self.data_cleaned = False
        self.graph_created = False
        self.communities_detected = False

    def get_valid_date(self, number_days=7):
        """
        Return valid date in string format and datetime format. A date is valid if it falls in the past 7 days
        otherwise it will be changed to the date 7 days ago. We can't get retweets from more than 7 days ago.
        """
        if datetime.strptime(self.since, "%Y-%m-%d").replace(tzinfo=tz) >= (
            datetime.now(tz=tz) - timedelta(days=number_days)
        ):
            self.min_date = self.since
            self.min_date_dt = datetime.strptime(self.since, "%Y-%m-%d").replace(tzinfo=tz)
        else:
            self.min_date = (datetime.now(tz=tz) - timedelta(days=number_days)).strftime(
                "%Y-%m-%d"
            )
            self.min_date_dt = datetime.now(tz=tz) - timedelta(days=number_days)

    def is_valid_tweet(self, tweet, source_tweet):
        """
        Is tweet valid i.e. :
        - the source tweet was published after the specified date in since (or in the last 7 days)
        - the number of retweet to consider is above the number of retweets specified in Class
        - the user is not retweeting or mentioning him/herself
        """
        return (
            (source_tweet.date > self.min_date_dt)
            & (tweet.user.username != source_tweet.user.username)
            & (source_tweet.retweetCount >= self.minretweets)
        )

    def create_search(self):
        """
        Create search string from keyword, type of search and since date. It must in format matching twitter requirements
        See https://github.com/igorbrigadir/twitter-advanced-search to get more details on how to perform advanced
        search in twitter.
        """
        search_final = f"{self.search} {self.type_search}"
        if self.min_date:
            search_final += f" since:{self.min_date}"
        return search_final

    def collect_tweets(self):
        """
        Collect and save tweets in nodes and edges files, for each tweet, the source tweet is also collected
        data collection stopped when their ist no longer tweet to collect or if the maximum number of tweets to collect
        is reached
        Tweets are saved in lists depending on the type of tweets (Retweet, quote or source tweet)
        Here we do not use snscrape cli command but directly its associated package through the TwitterSearchScraper
        module, thus the maxresults is not the same as in the cli command, here it refers to the maximum number of
        valid tweets (see the .is_valid_tweet() method to get a definition of valid tweet)
        """
        if not self.data_collected:
            self.data_collection_date = datetime.today()
            search = self.create_search()
            print(search)
            n_valid_tweet = 0
            for i, tweet in enumerate(
                sntwitter.TwitterSearchScraper(search).get_items()
            ):
                if i == 0:
                    self.most_recent_tweet = tweet.id
                is_RT_or_quoted = return_type_source_tweet(tweet)
                if is_RT_or_quoted:
                    source_tweet = return_source_tweet(tweet)
                    if self.is_valid_tweet(tweet, source_tweet):
                        self.edges.append(edge_from_tweet(tweet, source_tweet))
                        self.nodes_RT_quoted.append(node_RT_quoted(tweet, source_tweet))
                        if source_tweet.id not in self.nodes_original_done:
                            self.nodes_original.append(
                                node_original(tweet, source_tweet)
                            )
                            self.nodes_original_done.append(source_tweet.id)
                        n_valid_tweet += 1
                    self.last_collected_tweet = tweet.id
                    self.last_collected_date = tweet.date
                    if self.maxresults and n_valid_tweet >= self.maxresults:
                        break
            self.data_collected = True
        else:
            raise Exception(
                "Data has already been collected, rerun GaphBuilder class if you want to try with new"
                "parameter"
            )

    def clean_nodes_edges(self):
        """
        Clean node and edges files and delete old files that are not usefull anymore, to save memory
        Data is then stored in two dataframes, one containing nodes and the other containing edges
        """
        if self.data_collected:
            if len(self.edges):
                self.edges = clean_edges(self.edges, self.last_collected_date)
                #self.most_recent_tweet = self.edges[column_names.edge_source_date].max()
                if len(self.edges):
                    self.nodes = concat_clean_nodes(
                        self.nodes_RT_quoted,
                        self.nodes_original,
                        self.last_collected_date,
                    )
                    del self.nodes_original
                    del self.nodes_RT_quoted
                    self.data_cleaned = True
                else:
                    raise Exception(
                        "No enough tweets found to build graph. Try using other parameters "
                        "(for example decreasing the maximum number of retweets or extending the research window)"
                    )
            else:
                raise Exception(
                    "No enough tweets found to build graph. Try using other parameters "
                    "(for example decreasing the maximum number of retweets or extending the research window)"
                )
        else:
            raise Exception(
                "Data has not yet been collected, run .collect_tweets() before"
            )

    def create_graph(self, layout_algo="spring"):
        """
        Create graph object using networkx library and calculate positions of nodes using layout_algo
            Parameters:
                layout_algo (str): algorithm to use to create graph layout
                must be in ['circular', 'kamada_kawai', 'spring', 'random', 'spiral'])
        """
        if self.data_cleaned:
            self.G = nx.from_pandas_edgelist(
                self.edges, source="source", target="target", edge_attr="size"
            )
            position_function = layout_functions[layout_algo]["function"]
            self.positions = position_function(
                self.G, **layout_functions[layout_algo]["args"]
            )
            self.graph_created = True
        else:
            raise Exception(
                "data must be cleaned thanks to .clean_nodes_edges() before creating the graph"
            )

    def find_communities(self, community_algo="louvain"):
        """
        Find communities in graph using a community algorithm
            Parameters:
                community_algo (str): algorithm to use to find communities in the graph
                must be in ['greedy_modularity', 'asyn_lpa_communities', 'girvan_newman', 'label_propagation', 'louvain']
        """
        if self.graph_created:
            community_function = community_functions[community_algo]["function"]
            cleaning_function = community_functions[community_algo]["cleaning"]
            communities = community_function(
                self.G, **community_functions[community_algo]["args"]
            )
            self.communities = cleaning_function(communities)
            self.communities_detected = True
        else:
            raise Exception(
                "graph needs to be created thanks to .creat_graph() before using this command"
            )

    def export_img_graph(self, img_path="Graph.png"):
        """
        Export an image (png file) of the network
        It is a very basic image here you can juste visualise the connection between the nodes
            Parameters:
                 img_path (str): path where to export img file of the graph
        """
        if self.graph_created:
            plt.figure(figsize=(30, 30))
            nx.draw_networkx(
                self.G,
                pos=self.positions,
                arrows=True,
                with_labels=True,
                font_size=5,
                node_size=10,
                alpha=0.5,
            )
            plt.savefig(img_path, format="PNG")
        else:
            raise Exception(
                "graph needs to be created thanks to .creat_graph() before using this command"
            )

    def export_json_output(self, json_path="output.json"):
        """
        Create a clean json output containing the nodes, the edges and some other information (in metadata)
            Parameters:
                json_path (str): path where to export the json
        """
        if self.communities_detected:
            json_output = create_json_output(
                self.nodes, self.edges, self.positions, self.communities
            )
            json_output["metadata"] = {
                column_names.metadata_search: self.search,
                column_names.metadata_since: self.since,
                column_names.metadata_type_search: self.type_search,
                column_names.metadata_maxresults: self.maxresults,
                column_names.metadata_minretweets: self.minretweets,
                column_names.metadata_last_collected_tweet: self.last_collected_tweet,
                column_names.metadata_last_collected_date: str(self.last_collected_date),
                column_names.metadata_data_collection_date: str(self.data_collection_date),
                column_names.metadata_most_recent_tweet: str(self.most_recent_tweet),
            }
            with open(json_path, "w") as outfile:
                json.dump(json_output, outfile)
        else:
            raise Exception(
                "Before exporting json of the graph you must have run all functions to build it up:"
                "collect_tweets(), clean_nodes_edges(), create_graph() and find_communities()"
            )
