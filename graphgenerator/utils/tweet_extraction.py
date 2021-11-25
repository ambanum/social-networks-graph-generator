def edge_from_tweet(tweet):
    return {
        "source": tweet.user.username,
        "target": tweet.retweetedTweet.user.username,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id),
        "tweets": tweet.url,
        "label": "has quoted"
    }


def node_RT_from_tweet(tweet):
    return {
        "id": tweet.user.username,
        "label": "@" + tweet.user.username,
        "tweets": tweet.url,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id),
        "from": "quoted"
    }


def node_tweet_from_tweet(tweet):
    return {
        "id": tweet.retweetedTweet.user.username,
        "label": "@" + tweet.retweetedTweet.user.username,
        "tweets": tweet.retweetedTweet.url,
        "date": str(tweet.retweetedTweet.date),
        "tweet_id": str(tweet.retweetedTweet.id),
        "retweetCount": tweet.retweetCount,
        "from": "original"
    }