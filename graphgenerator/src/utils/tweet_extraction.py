def edge_from_tweet(tweet):
    return {
        "source": tweet.retweetedTweet.user.username,
        "target": str(tweet.user.username),
        "date": str(tweet.date),
        "tweet_id": str(tweet.id)
    }


def node_RT_from_tweet(tweet):
    return {
        "id": str(tweet.user.username),
        "label": tweet.user.username,
        "url": tweet.url,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id)
    }


def node_tweet_from_tweet(tweet):
    return {
        "id": str(tweet.retweetedTweet.user.username),
        "label": tweet.retweetedTweet.user.username,
        "url": tweet.retweetedTweet.url,
        "date": str(tweet.retweetedTweet.date),
        "tweet_id": str(tweet.retweetedTweet.id),
        "retweetCount": tweet.retweetCount,
    }