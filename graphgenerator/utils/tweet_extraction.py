def return_type_source_tweet(tweet):
    if tweet.retweetedTweet:
        return "has RT"
    elif tweet.quotedTweet:
        return "has quoted"
    else:
        return None


def return_source_tweet(tweet):
    if tweet.retweetedTweet:
        return tweet.retweetedTweet
    elif tweet.quotedTweet:
        return tweet.quotedTweet


def edge_from_tweet(tweet, source_tweet):
    return {
        "source": tweet.user.username,
        "target": source_tweet.user.username,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id),
        "tweets": tweet.url,
        "label": return_type_source_tweet(tweet),
    }


def node_RT_quoted(tweet):
    return {
        "id": tweet.user.username,
        "label": "@" + tweet.user.username,
        "tweets": tweet.url,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id),
        "from": return_type_source_tweet(tweet),
        "retweetCount": tweet.retweetCount if return_type_source_tweet(tweet) == "has quoted" else 0
    }


def node_original(tweet, source_tweet):
    return {
        "id": source_tweet.user.username,
        "label": "@" + source_tweet.user.username,
        "tweets": source_tweet.url,
        "date": str(source_tweet.date),
        "tweet_id": str(source_tweet.id),
        "retweetCount": tweet.retweetCount,
        "from": "original"
    }