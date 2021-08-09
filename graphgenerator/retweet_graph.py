# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:18:53 2021

@author: barre
"""
import os
import pandas as pd
from tqdm import tqdm
import networkx as nx

from graphgenerator import config


def research_tweet(search, since="2004-01-01", maxresults=4000, verbose=False):
    tmp_file = config.TMP_DIR / "search.json"

    cmd = 'snscrape --jsonl %s %s %s twitter-search "%s" > "%s"' % (
        "--progress" if verbose else "",
        "--max-results=%s" % (maxresults) if maxresults else "",
        "--since=%s" % (since) if since else "",
        search,
        tmp_file,
    )
    if verbose:
        print(cmd)
    os.system(cmd)
    tweets = pd.read_json(tmp_file, lines=True)
    os.remove(tmp_file)
    return tweets


def transformation_dataframe(dataframe):
    """Select the necessary information from the dataframe in entry and add an influence columns which is the sum of reply, retweet, like and quote counts
    Add a user column with all the required information"""
    reduced_dataframe = dataframe[
        [
            "content",
            "date",
            "id",
            "lang",
            "outlinks",
            "replyCount",
            "retweetCount",
            "likeCount",
            "quoteCount",
            # TODO Those columns are making the graph fail
            # "inReplyToUserId",
            # "inReplyToStatusId",
        ]
    ]
    influence_dataframe = pd.DataFrame(
        reduced_dataframe.loc[
            :, ["replyCount", "retweetCount", "likeCount", "quoteCount"]
        ].sum(axis=1),
        columns=["influence"],
    )
    user_list = list(dataframe["user"])
    user_dataframe = pd.DataFrame(user_list)[
        ["username", "displayname", "id", "followersCount", "location"]
    ]
    user_dataframe.columns = [
        "username",
        "displayname",
        "userid",
        "followersCount",
        "location",
    ]

    return pd.concat([reduced_dataframe, influence_dataframe, user_dataframe], axis=1)


def retweeter_graph(dataframe, retweets_minimal=10):
    """Return the retweeter graph (as a networkx graph)
    Parameters: retweets_minimal is the minimal number of tweets for which the twitter_api will fetch the list of retweeters"""
    retweet_dataframe = dataframe[dataframe["retweetCount"] > retweets_minimal]

    G = nx.Graph()
    problem_list = []
    # Adding Nodes
    for i, j, k in zip(
        retweet_dataframe["username"],
        retweet_dataframe["followersCount"],
        retweet_dataframe["influence"],
    ):
        G.add_node(i, Followers=j, Influence=k)

    # TODO use tqdm only if verbose mode is on
    # tqdm(
    #     zip(retweet_dataframe["id"], retweet_dataframe["username"])
    # )

    for tweet_id, retweeted_username in zip(retweet_dataframe["id"], retweet_dataframe["username"]):
        try:
            retweets_id = api.get_retweeter_ids(tweet_id)
            user_objects = api.lookup_users(user_id=retweets_id)
            for user in user_objects:
                retweeter_username = user.screen_name
                G.add_edge(retweeted_username, retweeter_username)
        except:
            problem_list.append(tweet_id)

    return (G, problem_list)


def graph_cli(search, since_date="2004-01-01", maxresults=4000, retweets_minimal=10,verbose=False):
    tweets = research_tweet(search, since_date, maxresults,verbose)
    tweets_transformed = transformation_dataframe(tweets)
    # The last line return a json compatible (with nx.node_link_data) representation of the retweet_graph -
    # The result of retweeter_graph being a list, it selects only the graph thus the 0
    return nx.node_link_data(retweeter_graph(tweets_transformed, retweets_minimal)[0])
