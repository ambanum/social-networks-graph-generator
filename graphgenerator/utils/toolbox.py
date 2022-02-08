import networkx as nx
from graphgenerator.config import column_names
import community as community_louvain
import networkx.algorithms.community as nxcom


layout_functions = {
    "bipartite": {"function": nx.bipartite_layout, "args": {}},
    "circular": {"function": nx.circular_layout, "args": {}},
    "kamada_kawai": {
        "function": nx.kamada_kawai_layout,
        "args": {"weight": column_names.edge_weight},
    },
    "planar": {"function": nx.planar_layout, "args": {}},
    "random": {"function": nx.random_layout, "args": {}},
    "shell": {"function": nx.shell_layout, "args": {}},
    "spring": {
        "function": nx.spring_layout,
        "args": {"weight": column_names.edge_weight},
    },
    "spectral": {"function": nx.spectral_layout, "args": {}},
    "spiral": {"function": nx.spiral_layout, "args": {}},
    "multipartite": {"function": nx.multipartite_layout, "args": {}},
}


def frozenset2partition_id(partition):
    """
    Transforms a frozenset object into clean partition user-id dict
    """
    partition_id = {}
    for i in range(len(partition)):
        for user_id in partition[i]:
            partition_id[user_id] = i
    return partition_id


def generator2partition_id(partition):
    """
    Transforms a generator object into clean partition user-id dict
    """
    partition = tuple(sorted(c) for c in next(partition))
    return frozenset2partition_id(partition)


def dict2partition_id(partition):
    """
    Transforms a dict object into clean partition user-id dict
    """
    return frozenset2partition_id(list(partition))


def ide(x):
    """
    identity function
    """
    return x


community_functions = {
    "greedy_modularity": {
        "function": nxcom.greedy_modularity_communities,
        "cleaning": frozenset2partition_id,
        "args": {"weight": column_names.edge_size},
    },
    "asyn_lpa_communities": {
        "function": nxcom.asyn_lpa_communities,
        "cleaning": frozenset2partition_id,
        "args": {"weight": column_names.edge_size},
    },
    "girvan_newman": {
        "function": nxcom.girvan_newman,
        "cleaning": generator2partition_id,
        "args": {},
    },
    "label_propagation": {
        "function": nxcom.label_propagation_communities,
        "cleaning": dict2partition_id,
        "args": {},
    },
    "louvain": {
        "function": community_louvain.best_partition,
        "cleaning": ide,
        "args": {"weight": column_names.edge_size},
    },
}
