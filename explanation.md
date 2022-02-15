# How do we generate an interaction graph?

Graphgenerator can recreate the network of interactions of Twitter accounts on a given hashtag or word (or group of words).

## Collecting tweets

The data is collected by Graphgenerator using the scraping tool [snscrape](https://github.com/JustAnotherArchivist/snscrape). This tool collects the data that is displayed when you search using the Twitter search bar. It only allows to retrieve the retweets of the **last seven days** (beyond that, only tweets and quotes can be collected).

Graphgenerator collects all tweets that are retweets or quotes of tweets mentioning the hashtag (or word or group of words) indicated in the search.

Only retweets and quotes for which the source tweet was published after the date of the last retweet or tweet quote are collected. This ensures that all retweets of a given tweet are available.

During data collection, Graphgenerator will also compute a bot score a the user level using the package [botfinder](https://github.com/ambanum/social-networks-bot-finder).

## Creation of the graph

Once the tweets are collected, they are rearranged to create links between the Twitter accounts.
Two Twitter accounts are linked if one quotes or retweets the other's tweet. A direction is attached to the link. Weights are allocated to each link and correspond to the number of occurrences of this link (total number of retweets and quotes from one account to the other).

The data is also aggregated at the account level which form the nodes of the graph. The size assigned to them corresponds to the total number of tweets and quotes of tweets issued by this account.

The data is put into graph format using the [Networkx](https://networkx.org/) library.

## Layout

To allow the good visualization of the graph, coordinates in a 2D (or 3D) plane are attributed to each nodes.

Several algorythms allow to compute the coordinates of the nodes of a graph to represent it as well as possible. The objective is to summarize the information in the graph as well as possible while making it readable. Generally the algorythms try to minimize the number of intersections of the links (for aesthetic considerations and to
ensure readability), to bring closer together the nodes that have many links between them and to place the "central" nodes in the center of the graph (which allow "central" nodes (which allow information to circulate within the network).

`networkx` command line provides many visualization possibilities and many of them are available in Graphgenerator. We propose to use by default the spring or [Fruchterman-Reingold](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html) algorithm because they works very well with large networks (which is our case).

The following layout algorithms are available in graphgenerator:
- Circular ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.circular_layout.html), [Wikipédia page](https://en.wikipedia.org/wiki/Circular_layout))
- Kamada Kawai ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html), [Wikipédia page](https://en.wikipedia.org/wiki/Force-directed_graph_drawing))
- Spring ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html))
- Random ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.random_layout.html), [Wikipédia page](https://en.wikipedia.org/wiki/Random_graph))
- Spiral ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spiral_layout.html))

## Communities

Graphgenerator also allows to identify clusters. They correspond to groups of accounts that interact a lot with each other.

Again, Networkx provides a wide choice of algorythms for identifying these communities, most of which are available in Graphgenerator.

By default, we have chosen an algorithm that is not available in Networkx but in an library. It is based on the "Leuven method". This method is particularly efficient for large networks.

The following algorithms are available in Graphgenerator:
- Greedy modularity ([doc](https://networkx.org/documentation/networkx-2.2/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html) )
- Asynchronous Label Propagation ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.label_propagation.asyn_lpa_communities.html))
- Girvan Newman ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.centrality.girvan_newman.html), [Wikipédia page](https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm))
- Label propagation ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.label_propagation.label_propagation_communities.html))
- Louvain ([doc](https://github.com/taynaud/python-louvain), [Wikipédia page](https://fr.wikipedia.org/wiki/M%C3%A9thode_de_Louvain))

## Enriching an existing graph

Using the `input_graph_json_path` command of `graphgenerator`, you can enrich an existing graph (`json` output of the `graphgenerator`). It will then use the parameters used to create the input graph to enrich it.

Existing graph must have been created in the last 7 days, otherwise the command won't work as only Retwwets from the last 7 days can be collected.


## Batch export

If the `batch_size` option is specified and > 0 then the graph is exported all the `batch_size` tweets collected. By default `batch_size` = 0, and in this case the graph is only exported once all data has been collected.

# Outputs

## JSON

Graphgenerator exports a json file containing information about the nodes (Twitter accounts, 'nodes') and the links between them ('edges').

The file contains three types of information

### Edges

List of links between Twitter accounts that mention the hashtag (accounts that retweet or quote the tweet of another account). For each link between accounts we have the following information:

- `source`: name of the twitter account that retweeted or quoted another account
- `target`: the retweeted or quoted account
- `size`: the size of the link, i.e. the number of quotes or RTs from 'source' to 'target
- `label`:
- `id`: the id of the link
- `type`:
- `metadata`: additional information about the link:
  - `date`: list of dates on which RTs or quotes occurred
  - `quoted`: list of links of quotes, in order of dates
  - `retweets`: list of RT links, by date order

### Nodes

List of twitter accounts that are quoted or RT or quote or RT a tweet containing the hashtag searched. For each account, we have the following information:

- `id`: account id
- `label`: username or twitter handle
- `size`: size of the node, i.e. number of times i was RT'd or quoted
- `from`: username or twitter handle
- `community_id`: id of the community detected thanks to the community algorithm
- `x`: x coordinate on the graph
- `y`: y coordinate on the graph
- `z`: y coordinate on the graph (if 3D option has been selected)
- `metadata`: additional information about the node:
  - `dates`: date of RTs, quotes or tweets from the account
  - `tweets`: list of urls of its tweets in ascending date order
  - `RT`: list of urls of its RTs in ascending date order
  - `quoted`: list of urls of its quotes in ascending order of dates
  - `dates_edges`: list of dates of RTs and quotes of this account (if any)
  - `botscore`: probability for the account to be a bot, computed thanks to [botfinder](https://github.com/ambanum/social-networks-bot-finder)

### Metadata

The `metadata` field contains additional information about the search and the results of the search performed.

- `search`: keyword or hashtag used in the search
- `since`: date until which the tweets were searched
- `maxresults`: maximum number of results in the search
- `minretweets`: minimum number of RTs in the search
- `last_collected_tweet`: id of the last collected tweets
- `last_collected_date`: date of the last collected tweet,
- `data_collection_date`: date of data collection
- `most_recent_tweet`: tweet id of the first collected tweet
- `execution_time`: total execution time
- `layout_algo`: algorithm used for layout
- `community_algo`: algorithm used to detect communities
- `n_collected_tweets`: number of collected tweets (that were used to build the graph)
- `n_analyzed_tweet`: number of analysed tweets (some tweets are not retweeted or mentionned and not included in the graph)
- `status`: data collection status (can be "in progress"  if the `batch_size` option is used)

## Graph

A png file can be exported using the `--img_path` command line option (or the
`export_img_graph()` method of `GraphBuilder`). The file allows you to quickly visualize the shape of the graph and thus test different types of layout.

## Example layout

Using the following command in the terminal:

```commandline
graphgenerator "#boycottfrance" --layout_algo "layout_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png?raw=true" --compute_botscore
```

or in your Python script

```commandline
from graphgenerator import GraphBuilder
import networkx as nx
import matplotlib.pyplot as plt


layout_algo = "spring" # or in ["kamada_kawai", "spiral", "circular", "random"]
GB = GraphBuilder(
    search = "#boycottfrance",
    since = "2021-12-02",
    minretweets = 1,
    maxresults = 1000
)
GB.collect_tweets()
GB.clean_nodes_edges()
GB.create_graph(layout_algo)

# Get graph using either GraphBuilder or networkx library + matplotlib
GB.export_graph("graph.png")
#or if you want to visualise the graph directly in your IDE (Jupyter Notebook for example)
plt.figure(figsize=(30, 30))
nx.draw_networkx(
    GB.G, pos=GB.positions, arrows=True, with_labels=True,
    font_size=5, node_size=10, alpha=0.5,
)

```

you get the following results (code was run on 09/12/2021):

|      Spiral Layout <br/>![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spiral.png?raw=true "Spiral")       |            Spring Layout <br/>![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spring.png?raw=true "Spring")             |
| :---------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------: |
| **Circular Layout** <br/> ![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_circular.png?raw=true "Circular") | **Kamada Kawai Layout** <br/> ![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_kamada_kawai.png?raw=true "Kamada Kawai") |
|    **Random Layout** <br/> ![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_random.png?raw=true "Random")    |

## Example community detection

Using the following code in the terminal (`"community_algo"` must be taken in  
`["greedy_modularity", "asyn_lpa_communities", "girvan_newman", "label_propagation", "louvain"]`) :

```commandline
graphgenerator "#boycottfrance" --layout_algo "spring" --community_algo "community_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png?raw=true"
```

Depending on the algorithm you use, you will get the following resultats (the color indicates the community)

|         Girvan Newman <br/>![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spring_girvan_newman.png?raw=true "Girvan Newmann")         | Greedy Modularity <br/>![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spring_greedy_modularity.png?raw=true "Greedy modularity") |
| :------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------: |
| **Label Propagation** <br/> ![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spring_label_propagation.png?raw=true "Label Propagation") |             **Louvain** <br/> ![alt](https://github.com/ambanum/social-networks-graph-generator/blob/main/img/%23boycottfrance_20211209_graph_spring_louvain.png?raw=true "Louvain")              |

---

[Lire en français](https://github.com/ambanum/social-networks-graph-generator/blob/main/explanation_fr.md)