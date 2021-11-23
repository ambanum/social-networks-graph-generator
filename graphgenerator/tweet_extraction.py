def edge_from_tweet(tweet):
    return {
        "source": tweet.retweetedTweet.user.id,
        "target": str(tweet.user.id),
        "date": str(tweet.date),
        "tweet_id": str(tweet.id)
    }


def node_RT_from_tweet(tweet):
    return {
        "id": str(tweet.user.id),
        "username": tweet.user.username,
        "url": tweet.url,
        "date": str(tweet.date),
        "tweet_id": str(tweet.id)
    }


def node_tweet_from_tweet(tweet):
    return {
        "id": str(tweet.retweetedTweet.user.id),
        "username": tweet.retweetedTweet.user.username,
        "url": tweet.retweetedTweet.url,
        "date": str(tweet.retweetedTweet.date),
        "tweet_id": str(tweet.retweetedTweet.id),
        "retweetCount": tweet.retweetCount,
    }