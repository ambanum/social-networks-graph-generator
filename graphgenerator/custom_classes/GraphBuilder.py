from datetime import datetime, timedelta
import json
import networkx as nx
import snscrape.modules.twitter as sntwitter
import matplotlib.pyplot as plt
from dateutil import parser
from math import sqrt, log

from graphgenerator.data_cleaning.edges import clean_edges
from graphgenerator.data_cleaning.nodes import concat_clean_nodes
from graphgenerator.data_cleaning.export import create_json_output
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

    def __init__(self, search, since, minretweets=1, maxresults=None, since_id=None, dim=2, compute_botscore=False):
        """
        Init function of class GraphBuilder
            Parameters:
                search (str): search you want to perform on Twitter (string that would type in twitter search bar)
                since (str): date in format %Y-%m-%d from where to start search, it must fall in the 7 last days
                otherwise it will be changed to the date 7 days ago (we can't get retweets from more than 7 days ago)
                minretweets (int): minimal number of retweets a tweet should have to be collected
                maxresults (int): maximum number of RT and quotes to include in the graph
                dim (int): dimension
                compute_botscore (bool): should botscore at the account level be computed or not
        """
        self.search = search
        self.minretweets = int(minretweets)
        self.maxresults = (
            None if (maxresults == "None") or (maxresults is None) else int(maxresults)
        )
        self.since = since
        self.since_id = since_id
        self.dim = dim
        self.compute_botscore = compute_botscore
        self.get_valid_date()
        self.nodes_original = []
        self.nodes_RT_quoted = []
        self.nodes_original_done = []
        self.type_search = "include:nativeretweets"
        self.edges = []
        self.edges_clean = []
        self.nodes = []
        self.G = []
        self.positions = []
        self.communities = {}
        self.last_collected_tweet = ""
        self.most_recent_tweet = ""
        self.data_collection_date = ""
        self.last_collected_date = ""
        self.layout_algo = ""
        self.community_algo = ""
        self.n_valid_tweet = 0
        self.n_analysed_tweets = 0
        self.data_collected = False
        self.data_cleaned = False
        self.graph_created = False
        self.communities_detected = False
        self.enough_data = True
        self.status = "PROCESSING"

    def get_valid_date(self, number_days=7):
        """
        Return valid date in string format and datetime format. A date is valid if it falls in the past 7 days
        otherwise it will be changed to the date 7 days ago. We can't get retweets from more than 7 days ago.
        """
        if datetime.strptime(self.since, "%Y-%m-%d").replace(tzinfo=tz) >= (
            datetime.now(tz=tz) - timedelta(days=number_days)
        ):
            self.min_date = self.since
            self.min_date_dt = datetime.strptime(self.since, "%Y-%m-%d").replace(
                tzinfo=tz
            )
        else:
            self.min_date = (
                datetime.now(tz=tz) - timedelta(days=number_days)
            ).strftime("%Y-%m-%d")
            self.min_date_dt = datetime.now(tz=tz) - timedelta(days=number_days)

    def is_valid_tweet(self, tweet, source_tweet, from_snscrape):
        """
        Is tweet valid i.e. :
        - the source tweet was published after the specified date in since (or in the last 7 days), not relevant if tweets are taken from snscrape json output 
        - the number of retweet to consider is above the number of retweets specified in Class
        - the user is not retweeting or mentioning him/herself
        """
        if from_snscrape:
            return (
                (tweet["user"]["username"] != source_tweet["user"]["username"])
                & (source_tweet["retweetCount"] >= self.minretweets)
            )
        else:
            if isinstance(source_tweet["date"], str):
                date_datetime = parser.parse(source_tweet["date"])
            else:
                date_datetime = source_tweet["date"]
            return (
                (date_datetime > self.min_date_dt)
                & (tweet["user"]["username"] != source_tweet["user"]["username"])
                & (source_tweet["retweetCount"] >= self.minretweets)
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
        if self.since_id:
            search_final += f" since_id:{self.since_id}"
        return search_final

    def extract_info_from_tweet(self, tweet, from_snscrape):
        """
        Extract information from a tweet and add to edges and nodes files
            Parameters:
                tweet (dict): a tweet in dictionnary format
                from_snscrape (str): path to snscrape path if relevant
        """
        is_RT_or_quoted = return_type_source_tweet(tweet)
        if is_RT_or_quoted:
            source_tweet = return_source_tweet(tweet)
            if self.is_valid_tweet(tweet, source_tweet, from_snscrape):
                self.edges.append(edge_from_tweet(tweet, source_tweet))
                self.nodes_RT_quoted.append(node_RT_quoted(tweet, source_tweet, self.compute_botscore))
                if source_tweet["id"] not in self.nodes_original_done:
                    self.nodes_original.append(
                        node_original(tweet, source_tweet, self.compute_botscore)
                    )
                    self.nodes_original_done.append(source_tweet["id"])
                self.n_valid_tweet += 1
            self.last_collected_tweet = tweet["id"]
            self.last_collected_date = tweet["date"]

    def save_batch(self, input_json, layout_algo, community_algo, img_path, json_path, execution_time):
        """
        """
        self.data_collected = True
        self.clean_nodes_edges(input_json)
        self.create_graph(layout_algo)
        self.find_communities(community_algo)
        if img_path != "no_img_file":
            self.export_img_graph(img_path)
        self.export_json_output(json_path, execution_time)

    def collect_tweets(self, snscrape_json_path=None, batch_size=0, **kwargs):
        """
        Collect and save tweets in nodes and edges files, for each tweet, the source tweet is also collected
        data collection stopped when their ist no longer tweet to collect or if the maximum number of tweets to collect
        is reached
        Tweets are saved in lists depending on the type of tweets (Retweet, quote or source tweet)
        Here we do not use snscrape cli command but directly its associated package through the TwitterSearchScraper
        module, thus the maxresults is not the same as in the cli command, here it refers to the maximum number of
        valid tweets (see the .is_valid_tweet() method to get a definition of valid tweet)
        Tweets can also be directy imported from output of snscrape command using arg `snscrape_json_path`
            Parameters:
                snscrape_json_path (str): path to snscrape json output from which to import tweets that will be used to build network, default is None
        """
        if not self.data_collected:
            self.data_collection_date = datetime.now(tz=tz)
            if snscrape_json_path:
                with open(snscrape_json_path, "r") as f:
                    for i,tweet in enumerate(f):
                        tweet_json = json.loads(tweet)
                        if i == 0:
                            self.most_recent_tweet = tweet_json["id"]
                        self.extract_info_from_tweet(tweet_json, snscrape_json_path)
                        self.n_analysed_tweets = i
            else:
                search = self.create_search()
                print(search)
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
                    tweet_json = json.loads(tweet.json())
                    if i == 0:
                        self.most_recent_tweet = tweet_json["id"]
                    self.extract_info_from_tweet(tweet_json, snscrape_json_path)
                    if self.maxresults and self.n_valid_tweet >= self.maxresults:
                        break
                    if batch_size>0 and self.n_valid_tweet%batch_size==0:
                        self.save_batch(
                            kwargs["input_json"], 
                            kwargs["layout_algo"], 
                            kwargs["community_algo"], 
                            kwargs["img_path"], 
                            kwargs["json_path"], 
                            kwargs["execution_time"]
                        )
                    self.n_analysed_tweets = i
            self.data_collected = True
            self.status = "DONE"
        else:
            raise Exception(
                "Data has already been collected, rerun GraphBuilder class if you want to try with new"
                "parameter"
            )

    def clean_nodes_edges(self, input_graph_json={}):
        """
        Clean node and edges files and delete old files that are not usefull anymore, to save memory
        Data is then stored in two dataframes, one containing nodes and the other containing edges
        If input_graph_json is not empty then it will merge the new nodes and edges to the old data contained
        in the input_graph_json file
            Parameters:
                input_graph_json (dict): graph in json format, output of grapgenerator command
        """
        if self.data_collected:
            if len(self.edges):
                self.edges_clean = clean_edges(
                    self.edges, self.last_collected_date, input_graph_json
                )
                if len(self.edges_clean) or input_graph_json:
                    self.nodes = concat_clean_nodes(
                        self.nodes_RT_quoted,
                        self.nodes_original,
                        self.last_collected_date,
                        input_graph_json,
                    )
                    #del self.nodes_original
                    #del self.nodes_RT_quoted
                    self.data_cleaned = True
                    self.enough_data = True
                else:
                    if input_graph_json:
                        raise Exception("No new data to add to existing graph")
                    else:
                        self.enough_data = False
            elif input_graph_json and len(self.edges) == 0:
                raise Exception("No new data to add to existing graph")
            else:
                self.enough_data = False
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
        self.layout_algo = layout_algo
        if self.enough_data:
            if self.data_cleaned:
                self.G = nx.from_pandas_edgelist(
                    self.edges_clean,
                    source=column_names.edge_source,
                    target=column_names.edge_target,
                    edge_attr=column_names.edge_size,
                )
                position_function = layout_functions[layout_algo]["function"]
                self.positions = position_function(
                    self.G, dim=self.dim, k=1/sqrt(self.G.number_of_nodes()), scale=200 + log(self.G.number_of_nodes())*300, **layout_functions[layout_algo]["args"]
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
        self.community_algo = community_algo
        if self.enough_data:
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
        if self.enough_data:
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

    def return_metadata_json(self, execution_time):
        """
        Create metadata dictionnary to be included in final json to export
            execution_time (datetime): execution time of the whole program 
        """
        return {
                column_names.metadata_search: self.search,
                column_names.metadata_since: self.min_date,
                column_names.metadata_type_search: self.type_search,
                column_names.metadata_maxresults: self.maxresults,
                column_names.metadata_minretweets: self.minretweets,
                column_names.metadata_last_collected_tweet: self.last_collected_tweet,
                column_names.metadata_last_collected_date: str(
                    self.last_collected_date
                ),
                column_names.metadata_data_collection_date: str(
                    self.data_collection_date
                ),
                column_names.metadata_most_recent_tweet: str(self.most_recent_tweet),
                column_names.metadata_execution_time: str(execution_time),
                column_names.metadata_layout_algo: self.layout_algo,
                column_names.metadata_community_algo: self.community_algo,
                column_names.metadata_n_collected_tweets: self.n_valid_tweet,
                column_names.metadata_n_analysed_tweets : self.n_analysed_tweets,
                column_names.metadata_status : self.status,
            }    

    def export_json_output(self, json_path="output.json", execution_time=float('nan')):
        """
        Create a clean json output containing the nodes, the edges and some other information (in metadata)
            Parameters:
                json_path (str): path where to export the json
                execution_time (datetime): execution time of the whole program 
        """
        if self.enough_data:
            if self.communities_detected:
                json_output = create_json_output(
                    self.nodes, self.edges_clean, self.positions, self.communities, self.dim
                )
                json_output["metadata"] = self.return_metadata_json(execution_time)
                with open(json_path, "w") as outfile:
                    json.dump(json_output, outfile)
            else:
                raise Exception(
                    "Before exporting json of the graph you must have run all functions to build it up:"
                    "collect_tweets(), clean_nodes_edges(), create_graph() and find_communities()"
                )
        else:
            json_output = {
                "edges": [],
                "nodes": []
            }
            json_output["metadata"] = self.return_metadata_json(execution_time)
            with open(json_path, "w") as outfile:
                json.dump(json_output, outfile)
