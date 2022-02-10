from graphgenerator.config import column_names
from botfinder.bot_classifier import findbot_rawjson
import json


def compute_bot_score_from_user_info(user_info, compute_botscore):
    """
    Compute botscore using botfinder using user information
    the function findbot_rawjson from the package is used rather than the CLI
    """
    if compute_botscore:
        return json.loads(findbot_rawjson(json.dumps(user_info)))["botScore"]
    else:
        return str(float("nan"))


def return_type_source_tweet(tweet: dict):
    """
    Returns type of a Tweet, returns:
    - "has RT" if it is a retweet
    - "has quoted" if it mentions another tweet
    - None if none of the previous case, in this case, the tweet is discarded from the graph construction
    """
    if tweet["retweetedTweet"]:
        return "has RT"
    elif tweet["quotedTweet"]:
        return "has quoted"
    else:
        return None


def return_source_tweet(tweet: dict):
    """
    Returns a Tweet which ist the source tweet of the given tweet (the tweet which has been retweeted or quoted)
    """
    if tweet["retweetedTweet"]:
        return tweet["retweetedTweet"]
    elif tweet["quotedTweet"]:
        return tweet["quotedTweet"]


def edge_from_tweet(tweet: dict, source_tweet: dict):
    """
    Create dictionnary from tweet (and its source tweet) information which will then feed the edge table
    Here tweets can be either retweet or quoted tweets, it describe the connexion between two accounts through a tweet
    """
    return {
        column_names.edge_source: tweet["user"]["username"],
        column_names.edge_target: source_tweet["user"]["username"],
        column_names.edge_source_date: source_tweet["date"],
        column_names.edge_date: str(tweet["date"]),
        column_names.edge_tweet_id: str(tweet["id"]),
        column_names.edge_url_quoted: tweet["url"]
        if return_type_source_tweet(tweet) == "has quoted"
        else "",
        column_names.edge_url_RT: tweet["url"]
        if return_type_source_tweet(tweet) == "has RT"
        else "",
        column_names.edge_url_label: return_type_source_tweet(tweet),
        column_names.edge_type: "arrow",
    }


def node_RT_quoted(tweet: dict, source_tweet: dict, compute_botscore: bool):
    """
    Create dictionnary containing nodes (account) information regarding an account which has retweeted
    or quoted another tweet
    """
    return {
        column_names.node_id: tweet["user"]["username"],
        column_names.node_label: "@" + tweet["user"]["username"],
        column_names.node_url_quoted: tweet["url"]
        if return_type_source_tweet(tweet) == "has quoted"
        else "",
        column_names.node_url_RT: tweet["url"]
        if return_type_source_tweet(tweet) == "has RT"
        else "",
        column_names.node_url_tweet: "",
        column_names.node_date: str(tweet["date"]),
        column_names.node_source_date: source_tweet["date"],
        column_names.node_tweet_id: str(tweet["id"]),
        column_names.node_type_tweet: return_type_source_tweet(tweet),
        column_names.node_rt_count: tweet["retweetCount"]
        if return_type_source_tweet(tweet) == "has quoted"
        else 0,
        column_names.node_botscore: compute_bot_score_from_user_info(tweet["user"], compute_botscore),
    }


def node_original(tweet: dict, source_tweet: dict, compute_botscore: bool):
    """
    Create dictionnary containing node (account) information regarding an account which has been retweeted
    or quoted in another tweet
    """
    return {
        column_names.node_id: source_tweet["user"]["username"],
        column_names.node_label: "@" + source_tweet["user"]["username"],
        column_names.node_url_tweet: source_tweet["url"],
        column_names.node_url_quoted: "",
        column_names.node_url_RT: "",
        column_names.node_date: source_tweet["date"],
        column_names.node_tweet_id: str(source_tweet["id"]),
        column_names.node_rt_count: tweet["retweetCount"],
        column_names.node_type_tweet: "original",
        column_names.node_botscore: compute_bot_score_from_user_info(source_tweet["user"], compute_botscore),
    }


def return_last_tweet_snscrape(snscrape_json_path: str):
    """
    Returns older collected tweet in snscrape json file 
    """
    with open(snscrape_json_path, "r") as f:
        for i,line in enumerate(f):
            last_tweet = json.loads(line)
    return last_tweet