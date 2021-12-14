import pandas as pd
from graphgenerator.config import column_names
from graphgenerator.config.config_export import (
    nodes_columns_metadata,
    edges_columns_metadata,
    edges_columns_export,
    nodes_columns_export,
)


def aggregate_edge_data(edges):
    """
    Aggregate edges data at the user level, to do so we use groupby command, data from a same column are  gathered
    in a list at the user level (except for the edge label for each we keep only the first label)
    """
    return (
        edges.groupby(
            [column_names.edge_source, column_names.edge_target, column_names.edge_type]
        )
        .agg(
            {
                column_names.edge_date: lambda x: list(x),
                column_names.edge_tweet_id: lambda x: list(x),
                column_names.edge_url_quoted: lambda x: list(x),
                column_names.edge_url_RT: lambda x: list(x),
                column_names.edge_size: lambda x: sum(x),
                column_names.edge_url_label: lambda x: list(x)[0],
            }
        )
        .reset_index()
    )


def input_graph_json2edge_df(input_graph_json):
    """
    Transform edge data from uploaded graph (in json version) into a dataframe to concatenate with new edges
    """
    edges = pd.DataFrame(input_graph_json["edges"])
    edges = edges.join(pd.json_normalize(edges["metadata"]))
    edges = edges.drop(["metadata", column_names.edge_id], axis=1)
    edges["table_id"] = 0
    return edges


def concatenate_old_n_new_edges(input_graph_json, new_edges):
    """
    Concatenate old edges taken from input_graph_json with new edges from data collection
    """
    old_edges = input_graph_json2edge_df(input_graph_json)
    new_edges["table_id"] = 1
    edges = pd.concat([new_edges, old_edges])
    edges = edges.sort_values("table_id")
    edges = edges.groupby([column_names.edge_source, column_names.edge_target, column_names.edge_type]).agg(
        {
            col: "sum" for col in [
            column_names.edge_size,
            column_names.edge_date,
            column_names.edge_url_RT,
            column_names.edge_url_quoted
        ]
        }
    ).reset_index()
    edges[column_names.edge_url_label] = "has RT/quoted"
    return edges


def clean_edges(edges_list, limit_date, input_graph_json):
    """
    Transform list of edges into a clean dataframe aggregated at the edge level (connexion between two accounts) and
    keep only if date of source tweet is after date of last collected tweet, to be sure that we have all RT and quote
    for a given tweet
    """
    edges = pd.DataFrame(edges_list)
    # keep only if source tweet is more recent thant last collected tweet
    edges = edges[edges[column_names.edge_source_date] > limit_date]
    # initialize edge size to 1
    edges[column_names.edge_size] = 1
    # sort by date
    edges = edges.sort_values(column_names.edge_date, ascending=True)
    # groupby id and aggregate all variables
    edges = aggregate_edge_data(edges)
    # merge with elder edges from input_graph_json
    if input_graph_json:
        edges = concatenate_old_n_new_edges(input_graph_json, edges)
    # create edge index
    edges = edges.reset_index().rename(columns={"index": column_names.edge_id})
    edges[column_names.edge_id] = "edge_" + edges[column_names.edge_id].astype(str)
    return edges


def clean_nodes_RT_quoted(nodes_RT_list, limit_date):
    """
    clean list of nodes extracted from retweets or tweets quoting other tweets and keep only if date
    of source tweet is after date of last collected tweet, to be sure that we have all RT and quote for a given tweet
    """
    nodes_RT = pd.DataFrame(nodes_RT_list)
    nodes_RT = nodes_RT.drop_duplicates()
    # keep only if source tweet is more recent thant last collected tweet
    nodes_RT = nodes_RT[nodes_RT[column_names.node_source_date] > limit_date]
    return nodes_RT


def clean_nodes_tweet(nodes_tweet_list, limit_date):
    """
    clean list of nodes extracted from tweets that have been retweeted or quoted in other tweets and keep only if date
    of source tweet is after date of last collected tweet, to be sure that we have all RT and quote for a given tweet
    """
    nodes_tweet = pd.DataFrame(nodes_tweet_list)
    nodes_tweet = nodes_tweet.drop_duplicates()
    # keep only if tweet is more recent thant last collected tweet
    nodes_tweet = nodes_tweet[nodes_tweet[column_names.node_date] > limit_date]
    nodes_tweet[column_names.node_date] = nodes_tweet[column_names.node_date].apply(str)
    return nodes_tweet


def drop_duplicated_nodes(nodes):
    """
    delete duplicated nodes and keep only the one with is "has quoted" (in some cases, it can happen that a tweet quote
    another tweet and is retweeted, in this specific case, we want to keep only the node from from the "has quoted"
    rather than the "original"
    (so we sort the data by the type of tweet so "has quoted" and "has RT" are before "original" and then we keep the
    first)
    //TO DO find best way to remove these duplicates, here it is quite dirty
    """
    nodes = nodes.sort_values(column_names.node_type_tweet, ascending=True)
    nodes = nodes.drop_duplicates(column_names.node_tweet_id, keep="first")
    return nodes


def aggregate_node_data(nodes):
    """
    sort by date and aggregate node data into list at the user level (the aggregated data are the data which
    will then be available in the metadata field)
    """
    nodes = nodes.sort_values(column_names.node_date, ascending=True)
    nodes = (
        nodes.groupby([column_names.node_id, column_names.node_label])
        .agg(
            {
                col: lambda x: list(x)
                for col in [
                    column_names.node_url_tweet,
                    column_names.node_url_quoted,
                    column_names.node_url_RT,
                    column_names.node_date,
                    #column_names.node_rt_count,
                    column_names.node_type_tweet,
                ]
            }
        )
        .reset_index()
    )
    return nodes


def deaggraggate_node_dataframe(old_nodes):
    """
    Nodes dataframe needs to be deaggragted as data are aggregate in lists at the user level
    In order to be reaggregated with the new data, it must be deaggragated
    To ensure that elements are aggregated in the right order at the user level (make sur that dates are ordered)
    To do so, intermediate table ist created for each column, it is deaggregated and merged with the user information
    Recreate column from based on list urls columns
    """
    old_nodes_deag = old_nodes[[column_names.node_label]].copy()
    i = 1
    for col in [
        column_names.node_date,
        column_names.node_url_tweet,
        column_names.node_url_quoted,
        column_names.node_url_RT
    ]:
        temp_data = old_nodes[col].apply(pd.Series).merge(
            old_nodes[[column_names.node_label]], left_index=True, right_index=True
        ).melt(
            id_vars=[column_names.node_label],
            value_name=col)
        if i == 1:
            old_nodes_deag = old_nodes_deag.merge(temp_data, how="right", on=column_names.node_label)
        else:
            old_nodes_deag = old_nodes_deag.merge(temp_data, how="right", on=[column_names.node_label, "variable"])
        i += 1
    old_nodes_deag = old_nodes_deag.dropna(how="any")

    #create colum 'from' with the type of tweet
    for col in column_names.col_mapping_type_tweet:
        old_nodes_deag.loc[
            old_nodes_deag[col].str.len() > 0, column_names.node_type_tweet
        ] = column_names.col_mapping_type_tweet[col]
        old_nodes_deag[col] = old_nodes_deag[col].apply(lambda x: x if len(x) else float("nan"))
    old_nodes_deag[column_names.node_tweet_id
    ] = old_nodes_deag["tweets"].fillna(old_nodes_deag["quoted"]).fillna(old_nodes_deag["retweets"])
    return old_nodes_deag


def input_graph_json2node_df(input_graph_json):
    """
    Transform output of graphgenerator into a dataframe containing informations related to the nodes
    Format must be similar to the dataframe produced by the cleaning functions after data collection
    It consists in doing the inverted process (deaggregate data) to allow for merging with new data
    """
    nodes = pd.DataFrame(input_graph_json["nodes"])
    nodes = nodes.join(pd.json_normalize(nodes["metadata"]))
    nodes = nodes.drop(["metadata"], axis=1)
    nodes["table_id"] = 0
    nodes = deaggraggate_node_dataframe(nodes)
    return nodes


def concat_clean_nodes(nodes_RT_quoted, nodes_original, limit_date, input_graph_json):
    """
    Concates nodes that are taken from tweets which are Retweets or tweets qu (nodes_RT_quoted) and original tweets which
    have been retweeted or quoted
    It then aggregate data to get only one row by account, data which cant be aggregated (summed up for ex) are gathered
    in a list
    It returns a unique file containing all nodes and attached information
    """
    # load nodes from RT and quoted tweets and from original tweets
    nodes_RT_quoted = clean_nodes_RT_quoted(nodes_RT_quoted, limit_date)
    nodes_original = clean_nodes_tweet(nodes_original, limit_date)
    nodes = pd.concat([nodes_original, nodes_RT_quoted])
    # aggregate retweet count at the user level to create a new variable which will be the size of the node
    # nodes[column_names.node_size] = nodes.groupby([column_names.node_id, column_names.node_label])[column_names.node_rt_count].transform('sum')
    #if input_graph, concatenate with new nodes
    if input_graph_json:
        old_nodes = input_graph_json2node_df(input_graph_json)
        nodes = pd.concat([nodes, old_nodes])
    # drop duplicates
    nodes = drop_duplicated_nodes(nodes)
    # aggregate data at the user level
    nodes = aggregate_node_data(nodes)
    # keep the first value of the type of tweet as a label
    nodes[column_names.node_type_tweet] = nodes[column_names.node_type_tweet].apply(
        lambda x: x[0]
    )
    return nodes


def merge_positions2nodes(position, nodes):
    """
    Merge positions data calculated thanks to layout algo in GraphBuilder to node dataframe
    """
    position_df = (
        pd.DataFrame(position)
        .T.reset_index()
        .rename(
            columns={
                0: column_names.node_pos_x,
                1: column_names.node_pos_y,
                "index": column_names.node_id,
            }
        )
    )
    nodes = nodes.merge(position_df, how="right", on=column_names.node_id)
    return nodes


def merge_communities2nodes(communities, nodes):
    """
    Merge communities data calculated thanks to community detection algo in Graphbuilder to node dataframe
    """
    communities_df = (
        pd.DataFrame([communities])
        .T.reset_index()
        .rename(
            columns={"index": column_names.node_id, 0: column_names.nodes_community}
        )
    )
    nodes = nodes.merge(communities_df, how="left", on=column_names.node_id)
    return nodes


def merge_edges_size_date2nodes(edges, nodes):
    """
    Sum up edge size at the use level to get the total number of RT and quotes of an user
    Use this method rather than summing up the RT count at the user level as it does not show all results (some RT are
    hidden and not returned in search function)
    It also aggregates all RT and quotes dates of an account to facilitate the creation of the graph (dates are sorted)
    """
    nodes_size_date = (
        edges[
            [column_names.edge_target, column_names.edge_size, column_names.edge_date]
        ]
        .groupby(column_names.edge_target)
        .agg({column_names.edge_size: "sum", column_names.edge_date: "sum"})
        .reset_index()
    )
    nodes_size_date = nodes_size_date.rename(
        columns={column_names.edge_date: column_names.node_edge_date}
    )
    nodes = nodes.merge(
        nodes_size_date,
        how="left",
        left_on=column_names.node_id,
        right_on=column_names.edge_target,
    )
    nodes[column_names.node_size] = nodes[column_names.node_size].fillna(0)
    nodes[column_names.node_edge_date] = nodes[column_names.node_edge_date].apply(
        lambda d: sorted(d) if isinstance(d, list) else []
    )
    return nodes


def create_json_output(nodes, edges, position, communities):
    """
    Create a json output with nodes and edges, merge positions and communities information at the user level
    """
    # merge nodes with other datasets
    nodes = merge_positions2nodes(position, nodes)
    nodes = merge_communities2nodes(communities, nodes)
    nodes = merge_edges_size_date2nodes(edges, nodes)
    # create metadata field in nodes en edges dataframes
    nodes[column_names.node_metadata] = nodes.apply(
        lambda x: {col: x[col] for col in nodes_columns_metadata}, axis=1
    )
    edges[column_names.edge_metadata] = edges.apply(
        lambda x: {col: x[col] for col in edges_columns_metadata}, axis=1
    )
    output = {
        "edges": edges[edges_columns_export].to_dict("records"),
        "nodes": nodes[nodes_columns_export].to_dict("records"),
    }
    return output
