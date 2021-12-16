import pandas as pd
from graphgenerator.config import column_names


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
        nodes.groupby([column_names.node_id, column_names.node_label, column_names.node_botscore])
        .agg(
            {
                col: lambda x: list(x)
                for col in [
                    column_names.node_url_tweet,
                    column_names.node_url_quoted,
                    column_names.node_url_RT,
                    column_names.node_date,
                    # column_names.node_rt_count,
                    column_names.node_type_tweet,
                ]
            }
        )
        .reset_index()
    )
    return nodes


def create_tweet_id_column(old_nodes):
    """
    Create tweet id column in old nodes dataframe using urls (tweet id is at the end of the url)
    """
    # create tweet id column from tweet url
    for col in [
        column_names.node_url_tweet,
        column_names.node_url_quoted,
        column_names.node_url_RT,
    ]:
        old_nodes[col] = old_nodes[col].apply(lambda x: x if len(x) else float("nan"))
    old_nodes[column_names.node_tweet_id] = (
        old_nodes["tweets"]
        .fillna(old_nodes["quoted"])
        .fillna(old_nodes["retweets"])
        .str.split("/")
        .str[-1]
    )
    for col in [
        column_names.node_url_tweet,
        column_names.node_url_quoted,
        column_names.node_url_RT,
    ]:
        old_nodes[col] = old_nodes[col].fillna("")
    return old_nodes


def create_from_column(old_nodes):
    """
    create colum 'from' with the type of tweet based on mapping with tweet url columns and its associated label
    """
    for col in column_names.col_mapping_type_tweet:
        old_nodes.loc[
            old_nodes[col].str.len() > 0, column_names.node_type_tweet
        ] = column_names.col_mapping_type_tweet[col]
    return old_nodes


def deaggraggate_node_dataframe(old_nodes):
    """
    Nodes dataframe needs to be deaggragted as data are aggregate in lists at the user level
    In order to be reaggregated with the new data, it must be deaggragated
    To ensure that elements are aggregated in the right order at the user level (make sur that dates are ordered)
    To do so, intermediate table ist created for each column, it is deaggregated and merged with the user information
    Recreate column from based on list urls columns
    """
    old_nodes_deag = old_nodes[[column_names.node_label, column_names.node_id, column_names.node_botscore]].copy()
    i = 1
    for col in [
        column_names.node_date,
        column_names.node_url_tweet,
        column_names.node_url_quoted,
        column_names.node_url_RT,
    ]:
        temp_data = (
            old_nodes[col]
            .apply(pd.Series)
            .merge(
                old_nodes[[column_names.node_label]], left_index=True, right_index=True
            )
            .melt(id_vars=[column_names.node_label], value_name=col)
        )
        if i == 1:
            old_nodes_deag = old_nodes_deag.merge(
                temp_data, how="right", on=column_names.node_label
            )
        else:
            old_nodes_deag = old_nodes_deag.merge(
                temp_data, how="right", on=[column_names.node_label, "variable"]
            )
        i += 1
    old_nodes_deag = old_nodes_deag.dropna(how="any")

    old_nodes_deag = create_from_column(old_nodes_deag)
    old_nodes_deag = create_tweet_id_column(old_nodes_deag)
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
    # if input_graph, concatenate with new nodes
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
