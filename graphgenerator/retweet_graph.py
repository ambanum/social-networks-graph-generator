# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 17:18:53 2021

@author: barre
"""
import os
import pandas as pd
from tqdm import tqdm
import networkx as nx


def research_tweet(search, date="2004-01-01", maxresults=4000):
    os.system(
        f'snscrape --jsonl --progress --max-results {maxresults} --since {date} twitter-search "{search}" > temporary.json'
    )
    tweets = pd.read_json("temporary.json", lines=True)
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
            "inReplyToUserId",
            "inReplyToStatusId",
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
        [
            "username",
            "displayname",
            "id",
            "followersCount",
            "location",
            "profileImageUrl",
        ]
    ]
    user_dataframe.columns = [
        "username",
        "displayname",
        "userid",
        "followersCount",
        "location",
        "profileImageUrl",
    ]

    return pd.concat([reduced_dataframe, influence_dataframe, user_dataframe], axis=1)


def retweeters(content):
    #The next lines remove some characters from the content analyze
    #This is because some characters are not correctly interpreted in the twitter search

    def replace(string) :
        for i in '''«»?!"-''' :
            string=string.replace(i, " ")
        return(string)
    content=replace(content)
    content=content.replace("\n"," ")
    
    os.system(
        f'snscrape --jsonl twitter-search "filter:nativeretweets {content}" > retweets.json'
    )
    
    s = pd.read_json("retweets.json", lines=True)
    username = list(s["user"].apply(lambda x: x["username"]))
    displayname = list(s["user"].apply(lambda x: x["displayname"]))
    image_url = list(s["user"].apply(lambda x: x["profileImageUrl"]))
    return username, displayname, image_url


def retweeter_graph(dataframe, retweet_min=10):
    """Return the retweeter graph (as a networkx graph)"""

    problem_list = []
    G = nx.Graph()
    node_dataframe = (
        dataframe[["influence", "username", "displayname", "profileImageUrl"]]
        .groupby(["username", "displayname", "profileImageUrl"])
        .sum(["influence"])
        .reset_index()
    )

    for username, displayname, influence, image_url in zip(
        node_dataframe["username"],
        node_dataframe["displayname"],
        node_dataframe["influence"],
        node_dataframe["profileImageUrl"],
    ):
        G.add_node(
            username,
            Displayname=displayname,
            Influence=influence,
            Image=image_url,
            label="Tweeting",
        )
    
    retweet_dataframe=dataframe[dataframe["retweetCount"] > retweet_min]
    for content,name in tqdm(zip(list(retweet_dataframe["content"]), list(retweet_dataframe["username"]))):
        try :
            (
                retweeter_i_username,
                retweeter_i_displayname,
                retweeter_i_image_url,
            ) = retweeters(content)
            for username, displayname, image_url in zip(
                retweeter_i_username, retweeter_i_displayname, retweeter_i_image_url
            ):
                if username not in G.nodes:
                    G.add_node(
                        username,
                        Displayname=displayname,
                        Image=image_url,
                        label="Not Tweeting",
                    )
            for username in retweeter_i_username:
                G.add_edge(name, username)
        except:
            #print('not ok', content)
            problem_list.append(content)
    return G, problem_list


def graph_cli_json(search, since_date="2004-01-01", maxresults=4000, retweet_min=10):
    tweets = research_tweet(search, since_date, maxresults)
    tweets_transformed = transformation_dataframe(tweets)
    # The last line return a json compatible (with nx.node_link_data) representation of the retweet_graph -
    # The result of retweeter_graph being a list, it selects only the graph thus the 0
    return nx.node_link_data(retweeter_graph(tweets_transformed, retweet_min=10)[0])

def graph_cli_gexf(search, since_date="2004-01-01", maxresults=4000, retweet_min=10):
    tweets = research_tweet(search, since_date, maxresults)
    tweets_transformed = transformation_dataframe(tweets)
    G,L=retweeter_graph(tweets_transformed, retweet_min=10)
    print('ok')
    nx.write_gexf(G, 'graph.gexf')
    print('\nok2')
    
