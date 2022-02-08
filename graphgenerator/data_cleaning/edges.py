import pandas as pd
from pyparsing import col
from graphgenerator.config import column_names


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
    edges = (
        edges.groupby(
            [column_names.edge_source, column_names.edge_target, column_names.edge_type]
        )
        .agg(
            {
                col: "sum"
                for col in [
                    column_names.edge_size,
                    column_names.edge_date,
                    column_names.edge_url_RT,
                    column_names.edge_url_quoted,
                ]
            }
        )
        .reset_index()
    )
    edges[column_names.edge_url_label] = "has RT/quoted"
    return edges


def calculate_edges_weight(edges, node_size_weight=0.5):
    """
    Calculate edge weight based on node size from source and target
        node_size_weight (float): weight of node size in the computation of the final weight
    """
    edges_size = edges[[column_names.edge_target, column_names.edge_size]].groupby(column_names.edge_target).agg(sum)
    edges_size = edges_size.rename(columns={column_names.edge_size: "temp_size"})
    edges = edges.merge(edges_size, how="left", left_on=column_names.edge_target, right_on=column_names.edge_target)
    edges = edges.merge(edges_size, how="left", left_on=column_names.edge_source, right_on=column_names.edge_target)
    for col in ['temp_size_x', 'temp_size_y']:
        edges[col] = edges[col].fillna(0)
    normalized_size = edges[column_names.edge_size]/edges[column_names.edge_size].max()
    edges[column_names.edge_weight] =  node_size_weight*(1/(edges["temp_size_x"]+edges["temp_size_y"])) + (1-node_size_weight)*normalized_size
    edges = edges.drop(['temp_size_x', 'temp_size_y'], axis = 1)
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
    #calculate edge weight
    edges = calculate_edges_weight(edges)
    # create edge index
    edges = edges.reset_index().rename(columns={"index": column_names.edge_id})
    edges[column_names.edge_id] = "edge_" + edges[column_names.edge_id].astype(str)
    return edges
