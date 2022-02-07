from graphgenerator.config import column_names


nodes_columns_metadata = [
    column_names.node_date,
    column_names.node_url_tweet,
    column_names.node_url_quoted,
    column_names.node_url_RT,
    column_names.node_edge_date,
    column_names.node_botscore
]

edges_columns_metadata = [
    column_names.node_date,
    column_names.node_url_quoted,
    column_names.node_url_RT,
]


edges_columns_export = [
    column_names.edge_source,
    column_names.edge_target,
    column_names.edge_size,
    column_names.edge_url_label,
    column_names.edge_id,
    column_names.edge_type,
    column_names.edge_metadata,
]

nodes_columns_export = {
    2: [
        column_names.node_id,
        column_names.node_label,
        column_names.node_size,
        column_names.node_type_tweet,
        column_names.node_metadata,
        column_names.node_pos_x,
        column_names.node_pos_y,
        column_names.nodes_community,
    ],
    3:[
        column_names.node_id,
        column_names.node_label,
        column_names.node_size,
        column_names.node_type_tweet,
        column_names.node_metadata,
        column_names.node_pos_x,
        column_names.node_pos_y,
        column_names.node_pos_z,
        column_names.nodes_community,
    ]
}
