import pandas as pd


def clean_edges(edges_list):
    edges = pd.DataFrame(edges_list)
    edges = edges[edges["source"] != edges["target"]]
    edges["size"] = 1
    edges = edges.groupby(["source", "target", "label"]).agg(
        {"date": lambda x: list(x), "tweet_id": lambda x: list(x), "tweets": lambda x: list(x), "size": lambda x: sum(x)}
    ).reset_index()
    edges["type"] = "arrow"
    edges = edges.reset_index().rename(columns= {"index": "id"})
    edges["id"] = "edge_" + edges["id"].astype(str)
    return edges


def clean_nodes_RT(nodes_RT_list):
    nodes_RT = pd.DataFrame(nodes_RT_list)
    nodes_RT = nodes_RT.drop_duplicates()
    nodes_RT["retweetCount"] = 0
    return nodes_RT


def clean_nodes_tweet(nodes_tweet_list):
    nodes_tweet = pd.DataFrame(nodes_tweet_list)
    nodes_tweet = nodes_tweet.drop_duplicates()
    return nodes_tweet


def create_json_output(nodes, edges, position):
    position_df = pd.DataFrame(position).T.reset_index().rename(columns={0: "x", 1: "y", "index": "id"})
    nodes = nodes.merge(position_df, how="right", on="id")

    nodes["metadata"] = nodes.apply(
        lambda x: {col: x[col] for col in ['date', "tweets"]}, axis=1
    )
    edges["metadata"] = edges.apply(lambda x: {col: x[col] for col in ['date', "tweets"]}, axis=1)
    output = {
        "edges": edges[['source', 'target', 'size', 'label', "id", "type", 'metadata']].to_dict('records'),
        "nodes": nodes[['id', 'label', 'size', 'from', 'metadata', 'x', 'y']].to_dict('records')
    }
    return output