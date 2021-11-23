import pandas as pd


def clean_edges(edges_list):
    edges = pd.DataFrame(edges_list)
    edges["size"] = 1
    edges = edges.groupby(["source", "target"]).agg(
        {"date": lambda x: list(x), "tweet_id": lambda x: list(x), "size": lambda x: sum(x)}
    ).reset_index()
    edges["label"] = "retweeted"
    return edges


def clean_nodes_RT(nodes_RT_list):
    nodes_RT = pd.DataFrame(nodes_RT_list)
    nodes_RT["retweetCount"] = 0
    nodes_RT["size"] = 1
    nodes_RT["role"] = "RT"
    return nodes_RT


def clean_nodes_tweet(nodes_tweet_list):
    nodes_tweet = pd.DataFrame(nodes_tweet_list)
    nodes_tweet['size'] = nodes_tweet.groupby(
        ['id', 'username'])['retweetCount'].transform('sum')
    nodes_tweet["role"] = "Tweet"
    return nodes_tweet


def create_json_output(nodes, edges, position):
    position_df = pd.DataFrame(position).T.reset_index().rename(columns={0: "x", 1: "y", "index": "id"})
    nodes = nodes.merge(position_df, how="right", on="id")
    nodes["metadata"] = nodes.apply(
        lambda x: {col: x[col] for col in ['date', "tweet_id", "retweetCount", "role", "url"]}, axis=1
    )
    edges["metadata"] = edges.apply(lambda x: {col: x[col] for col in ['date', "tweet_id"]}, axis=1)
    output = {
        "edges": edges[['source', 'target', 'size', 'label', 'metadata']].to_dict('records'),
        "nodes": nodes[['id', 'username', 'size', 'metadata']].to_dict('records')
    }
    return output