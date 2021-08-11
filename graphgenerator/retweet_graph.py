import os
import pandas as pd
import networkx as nx

#Remove undue warnings
pd.options.mode.chained_assignment = None

#Those two list of strings are useful afterwards to find information
user_features_to_extract = [
    "username",
    "displayname",
    "verified",
    "followersCount",
    "friendsCount",
    "statusesCount",
    "favouritesCount",
    "profileImageUrl",
]

attention_columns = ["replyCount", "retweetCount", "likeCount", "quoteCount"]



def research_tweet(
    search, since=None, maxresults=None, verbose=False, minretweets=None
):
    cmd = "snscrape --jsonl"
    if verbose:
        cmd += " --progress "
    if maxresults:
        if not isinstance(maxresults, int):
            raise Exception("maxresults must be an integer")
        cmd += f" --max-results {maxresults} "
    if since:
        if not isinstance(since, str):
            raise Exception("since must be a string")
        cmd += f" --since {since} "

    cmd += f" twitter-search include:nativeretweets{search} > temporary.json"

    os.system(cmd)
    tweets = pd.read_json("temporary.json", lines=True)
    os.remove("temporary.json")
    return tweets

def extract_user_info(dataframe):
    for i in user_features_to_extract:
        dataframe[i] = dataframe["user"].apply(lambda x: x[i])
    return dataframe


def transformation_user_dataframe(dataframe):
    """This function takes in entry a dataframe corresponding to a snscrape research and return
    a dataframe containing all its user (with no duplicates). The following information are contained in
    the dataframe : username, displayname, verified, followersCount, friendsCount, statusesCount,
    favouritesCount, profileImageUrl"""

    # We will merge four different dataframes of tweets
    # First one is the data concerning the tweets which are not retweets
    not_retweet_user_dataframe = dataframe[dataframe["retweetedTweet"].isnull()]
    not_retweet_user_dataframe = extract_user_info(not_retweet_user_dataframe)

    # Second one is the one constituted of all retweeters :
    # the attention score for these retweets is taken to be 0
    retweeter_user_dataframe = dataframe[dataframe["retweetedTweet"].notnull()]
    retweeter_user_dataframe = extract_user_info(retweeter_user_dataframe)
    for i in attention_columns:
        retweeter_user_dataframe[i] = 0

    # Third one is the tweets who have been retweeted : we have to fetch their attention score
    # and the user features to include in the nodes
    retweeted_user_dataframe = dataframe[dataframe["retweetedTweet"].notnull()]
    retweeted_user_dataframe["id"] = retweeted_user_dataframe["retweetedTweet"].apply(
        lambda x: x["id"]
    )
    retweeted_user_dataframe = retweeted_user_dataframe.drop_duplicates(subset=["id"])
    for i in user_features_to_extract:
        retweeted_user_dataframe[i] = retweeted_user_dataframe["retweetedTweet"].apply(
            lambda x: x["user"][i]
        )
    for i in attention_columns:
        retweeted_user_dataframe[i] = retweeted_user_dataframe["retweetedTweet"].apply(
            lambda x: x[i]
        )

    # Fourth one is the quoted tweets 
    
    quoted_user_dataframe = dataframe[dataframe["retweetedTweet"].isnull()]
    quoted_user_dataframe = quoted_user_dataframe[quoted_user_dataframe["quotedTweet"].notnull()]
    quoted_user_dataframe["id"] = quoted_user_dataframe["quotedTweet"].apply(
        lambda x: x["id"]
    )
    quoted_user_dataframe = quoted_user_dataframe.drop_duplicates(subset=["id"])
    for i in user_features_to_extract:
        quoted_user_dataframe[i] = quoted_user_dataframe["quotedTweet"].apply(
            lambda x: x["user"][i]
        )
    for i in attention_columns:
        quoted_user_dataframe[i] = quoted_user_dataframe["quotedTweet"].apply(
            lambda x: x[i]
        )

    
    #Finally we concatenate all those dataframes

    final_dataframe = pd.concat(
        [not_retweet_user_dataframe, retweeter_user_dataframe, retweeted_user_dataframe, quoted_user_dataframe]
    )
    final_dataframe = final_dataframe[
        ["id", "date"] + user_features_to_extract + attention_columns
    ]
    # We change the hour to be importable in gefx :
    final_dataframe["date"] = final_dataframe["date"].apply(
        lambda x: (x.round(freq="H")).strftime("%Y-%m-%d-%H")
    )
    
    # The final step is tricky : we want to add the values of attention_columns and keep the users_features
    # We have to use aggregate and groupby, see the docs
    aggregation_functions ={}
    for i in ['date', 'id']+user_features_to_extract :
        aggregation_functions[i] = 'first'
    for i in attention_columns : 
        aggregation_functions[i] = 'sum'
        
    final_dataframe= final_dataframe.groupby(final_dataframe['username']).agg(aggregation_functions)
    final_dataframe=final_dataframe.drop(columns=['id'])
    return final_dataframe

def transformation_retweet_dataframe(dataframe):
    """This function takes in entry a dataframe corresponding to a snscrape research and return
    a dataframe containing the retweets within the search. The following information is contained in the returned
    dataframe : retweeterUsername, retweetedUsername, dateRetweet and label ('retweet' or 'quote')"""
    # Selecting the lines of the tweets which are quote tweet
    retweet_dataframe = dataframe[dataframe["retweetedTweet"].notnull()]
    # Dropping useless columns
    retweet_dataframe = retweet_dataframe[["retweetedTweet", "user", "date"]]
    retweet_dataframe["retweeterUsername"] = retweet_dataframe["user"].apply(
        lambda x: x["username"]
    )
    retweet_dataframe["retweetedUsername"] = retweet_dataframe["retweetedTweet"].apply(
        lambda x: x["user"]["username"]
    )
    # Round up to hour
    # The panda Timestamp format is changed into a string for the gexf export at the end
    retweet_dataframe["date"] = retweet_dataframe["date"].apply(
        lambda x: (x.round(freq="H")).strftime("%Y-%m-%d-%H")
    )
    retweet_dataframe = retweet_dataframe.drop(columns=["user", "retweetedTweet"])
    retweet_dataframe['category'] = 'retweet'
    return retweet_dataframe

def transformation_quoted_dataframe(dataframe):
    """This function takes in entry a dataframe corresponding to a snscrape research and return
    a dataframe containing the quoted tweets within the search. The following information is contained in the returned
    dataframe : quoterUsername, quotedUsername, dateRetweet and label ('retweet' or 'quote')"""
    # Selecting the lines of the tweets which are quote tweet but not retweet
    quoted_dataframe = dataframe[dataframe["retweetedTweet"].isnull()]
    quoted_dataframe = quoted_dataframe[quoted_dataframe["quotedTweet"].notnull()]
    # Dropping useless columns
    quoted_dataframe = quoted_dataframe[["quotedTweet", "user", "date"]]
    quoted_dataframe["retweeterUsername"] = quoted_dataframe["user"].apply(
        lambda x: x["username"]
    )
    quoted_dataframe["retweetedUsername"] = quoted_dataframe["quotedTweet"].apply(
        lambda x: x["user"]["username"]
    )
    # Round up to hour
    # The panda Timestamp format is changed into a string for the gexf export at the end

    quoted_dataframe["date"] = quoted_dataframe["date"].apply(
        lambda x: (x.round(freq="H")).strftime("%Y-%m-%d-%H")
    )
    quoted_dataframe = quoted_dataframe.drop(columns=["user", "quotedTweet"])
    quoted_dataframe["category"] = 'quote'
    return quoted_dataframe

def retweeter_graph(dataframe, graph=None, remove=None):
    """Return the retweeter graph (as a networkx graph)
    if remove : will remove the nodes whose degree is less than 2"""

    if graph:
        if not isinstance(graph, nx.Graph()):
            raise Exception("graph must be a networkx graph")
    else:
        graph = nx.Graph()

    retweet_dataframe = transformation_retweet_dataframe(dataframe)
    quoted_dataframe = transformation_quoted_dataframe(dataframe)

    # This is the graph with the edges and their attributes
    new_graph = nx.convert_matrix.from_pandas_edgelist(
        pd.concat([retweet_dataframe, quoted_dataframe]),
        source="retweeterUsername",
        target="retweetedUsername",
        edge_attr=True,
    )

    user_dataframe = transformation_user_dataframe(dataframe)
    # We have to transform the dataframe in a dictionnary of dictionnary in order to use it as an argument for
    # the node definition in networkx
    node_dictionnary = user_dataframe.to_dict(orient="index")
    nx.set_node_attributes(new_graph, node_dictionnary)
    
    # We fuse the last graphs together
    # Where the attributes conflict, it uses the attributes of the second argument ; for the date of the edges it will thus take the last

    final_graph = nx.algorithms.operators.binary.compose(graph, new_graph)
    
    def remove_degree_less_than(graph, n) :
        iter_nodes = graph.degree()
        for node_name, node_degree in list(iter_nodes) :
            if node_degree < n :
                graph.remove_node(node_name)
                #also removes the edges
            
    if remove :
        if not isinstance(remove, int) :
            raise Exception("remove must be an integer")
        remove_degree_less_than(final_graph, remove)
        
        

    return final_graph