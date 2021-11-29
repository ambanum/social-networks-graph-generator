import pandas as pd
from graphgenerator.config import column_names
from graphgenerator.config.config_export import nodes_columns_metadata, edges_columns_metadata, edges_columns_export, \
    nodes_columns_export


def clean_edges(edges_list):
    """
    Transform list of edges into a clean dataframe aggregated at the edge level (connexion between two accounts)
    """
    edges = pd.DataFrame(edges_list)
    #edges = edges[edges["source"] != edges["target"]]
    edges[column_names.edge_size] = 1
    edges = edges.groupby([column_names.edge_source, column_names.edge_target, column_names.edge_type]).agg(
        {column_names.edge_date: lambda x: list(x), column_names.edge_tweet_id: lambda x: list(x),
         column_names.edge_url_quoted: lambda x: list(x), column_names.edge_url_RT: lambda x: list(x),
         column_names.edge_size: lambda x: sum(x), column_names.edge_url_label: lambda x: list(x)[0]}
    ).reset_index()
    #create edge index
    edges = edges.reset_index().rename(columns= {"index": column_names.edge_id})
    edges[column_names.edge_id] = "edge_" + edges[column_names.edge_id].astype(str)
    return edges


def clean_nodes_RT_quoted(nodes_RT_list):
    """
    clean list of nodes extracted from retweets or tweets quoting other tweets
    """
    nodes_RT = pd.DataFrame(nodes_RT_list)
    nodes_RT = nodes_RT.drop_duplicates()
    return nodes_RT


def clean_nodes_tweet(nodes_tweet_list):
    """
    clean list of nodes extracted from tweets that have been retweeted or quoted in other tweets
    """
    nodes_tweet = pd.DataFrame(nodes_tweet_list)
    nodes_tweet = nodes_tweet.drop_duplicates()
    return nodes_tweet


def drop_duplicated_nodes(nodes):
    """
    delete duplicated nodes and keep only the one with is "has quoted" (in some cases, it can happen that a tweet quote
    another tweet and is retweeted, in this specific case, we want to keep only the node from from the "has quoted"
    rather than the "original"
    """
    nodes = nodes.sort_values(column_names.node_type_tweet, ascending=True)
    nodes = nodes.drop_duplicates(column_names.node_tweet_id, keep="first")
    return nodes


def aggregate_node_data(nodes):
    """
    sort by date and aggregate data into list at the user level (will then be available in metadata field)
    """
    nodes = nodes.sort_values(column_names.node_date, ascending=True)
    nodes = nodes.groupby([column_names.node_id, column_names.node_label, column_names.node_size]).agg(
        {col: lambda x: list(x) for col in [column_names.node_url_tweet, column_names.node_url_quoted,
                                            column_names.node_url_RT, column_names.node_date,
                                            column_names.node_rt_count, column_names.node_type_tweet]}
    ).reset_index()
    return nodes

def concat_clean_nodes(nodes_RT_quoted, nodes_original):
    """
    Concates nodes that are taken from tweets which are Retweets or tweets qu (nodes_RT_quoted) and original tweets which
    have been retweeted or quoted
    It then aggregate data to get only one row by account, data which cant be aggregated (summed up for ex) are gathered
    in a list
    It returns a unique file containing all nodes and attached information
    """
    #load nodes from RT and quoted tweets and from original tweets
    nodes_RT_quoted = clean_nodes_RT_quoted(nodes_RT_quoted)
    nodes_original = clean_nodes_tweet(nodes_original)
    nodes = pd.concat([nodes_original, nodes_RT_quoted])
    #drop duplicates
    nodes = drop_duplicated_nodes(nodes)
    #aggregate retweet count at the user level to create a new variable which will be the size of the node
    nodes[column_names.node_size] = nodes.groupby([column_names.node_id, column_names.node_label])[column_names.node_rt_count].transform('sum')
    #aggregate data at the user level
    nodes = aggregate_node_data(nodes)
    #keep the first value of the type of tweet as a label
    nodes[column_names.node_type_tweet] = nodes[column_names.node_type_tweet].apply(lambda x: x[0])
    return nodes


def create_json_output(nodes, edges, position):
    """
    Create a json output with nodes and edges
    """
    position_df = pd.DataFrame(position).T.reset_index().rename(
        columns={0: column_names.node_pos_x, 1: column_names.node_pos_y, "index": column_names.node_id}
    )
    nodes = nodes.merge(position_df, how="right", on=column_names.node_id)

    nodes[column_names.node_metadata] = nodes.apply(lambda x: {col: x[col] for col in nodes_columns_metadata}, axis=1)
    edges[column_names.edge_metadata] = edges.apply(lambda x: {col: x[col] for col in edges_columns_metadata}, axis=1)
    output = {
        "edges": edges[edges_columns_export].to_dict('records'),
        "nodes": nodes[nodes_columns_export].to_dict('records')
    }
    return output
