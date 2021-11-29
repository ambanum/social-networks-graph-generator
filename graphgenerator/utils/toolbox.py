import networkx as nx
from graphgenerator.config import column_names


layout_functions = {
    "bipartite":{"function": nx.bipartite_layout, "args": {}},
    "circular": {"function": nx.circular_layout,  "args": {}},
    "kamada_kawai": {"function": nx.kamada_kawai_layout, "args": {"weight": column_names.edge_size}},
    "planar": {"function": nx.planar_layout,  "args": {}},
    "random": {"function": nx.random_layout,  "args": {}},
    "shell": {"function": nx.shell_layout,  "args": {}},
    "spring": {"function": nx.spring_layout, "args": {"weight": column_names.edge_size}},
    "spectral": {"function": nx.spectral_layout,  "args": {}},
    "spiral": {"function": nx.spiral_layout,  "args": {}},
    "multipartite": {"function": nx.multipartite_layout, "args": {}}
}