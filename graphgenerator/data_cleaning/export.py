import pandas as pd
from graphgenerator.config import column_names
from graphgenerator.config.config_export import (
    nodes_columns_metadata,
    edges_columns_metadata,
    edges_columns_export,
    nodes_columns_export,
)


def merge_positions2nodes(position, nodes, dim):
    """
    Merge positions data calculated thanks to layout algo in GraphBuilder to node dataframe
    """
    columns_mapping = {
                    0: column_names.node_pos_x,
                    1: column_names.node_pos_y,
                    "index": column_names.node_id,
                }
    if dim == 3:
        columns_mapping[2] = column_names.node_pos_z
    position_df = (
        pd.DataFrame(position)
        .T.reset_index()
        .rename(
            columns=columns_mapping
        )
    )
    nodes = nodes.merge(position_df, how="right", on=column_names.node_id)
    nodes[column_names.node_pos_y] = nodes[column_names.node_pos_y] #*800/2
    nodes[column_names.node_pos_x] = nodes[column_names.node_pos_x] #*800/2
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


def create_json_output(nodes, edges, position, communities, dim):
    """
    Create a json output with nodes and edges, merge positions and communities information at the user level
    """
    # merge nodes with other datasets
    nodes = merge_positions2nodes(position, nodes, dim)
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
        "nodes": nodes[nodes_columns_export[dim]].to_dict("records"),
    }
    return output
