# Methodology

Graphgenerator can recreate the network of interactions of Twitter accounts on a given hashtag or word (or group of words) 
given. 

## Collecting tweets

The data is collected by `Graphgenerator` using the collection tool `snscrape`. This tool collects the data
that is displayed when you search in the Twitter search bar. It only allows to retrieve 
the retweets of the last seven days (beyond that only tweets and mentions can be collected). The 
collection is limited to the last seven days.

`Graphgenerator` collects all tweets that are retweets or mentions of tweets mentioning the hashtag 
(or word or group of words) indicated in the search. 
group of words) indicated in the search.

Only retweets and mentions for which the source tweet was published after the date of the last retweet or 
tweet mention are collected. This ensures that all retweets of a given tweet are available. 

## Creation of the graph

Once the tweets are collected, they are rearranged to create links between the Twitter accounts.
Two Twitter accounts are linked if one mentions or retweets the other's tweet. A direction is attached 
to the link. Weights are allocated to each link and correspond to the number of occurrences of this link (total number of retweets and 
mentions from one account to the other). 

The data are also aggregated at the account level which form the nodes of the graph. The size assigned to them 
corresponds to the total number of tweets and mentions of tweets issued by this account.

The data is put into graph format using the `networkx` library.

## Layout

To allow the good visualization of the graph, coordinates in a 2D (or 3D) plane are attributed to each 
nodes.

Several algorithms allow to compute the coordinates of the nodes of a graph to represent it as well as possible. 
The objective is to summarize the information in the graph as well as possible while making it readable. 
Generally the algorithms try to minimize the number of intersections of the links (by aesthetic consideration, 
of readability), to bring closer together the nodes that have many links between them and to place the "central" nodes in the center of the graph (which allow
"central" nodes (which allow information to circulate within the network).

`networkx` provides many visualization possibilities and many of them are available in Graphgenerator. 
We propose to use by default the spring or Fruchterman-Reingold (https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html) aglorithm.
It works very well with large networks (which is our case).

## Communities

`Graphgenerator` also allows to identify clusters. They correspond to groups of accounts that interact 
a lot with each other. 

Again, `networkx` provides a wide choice of algorithms for identifying these communities, most of which are 
available in `graphgenerator`. 

By default, we have chosen an algorithm that is not available in `networkx` but in an 
library. It is based on the "Leuven method". This method is particularly efficient for large networks.

#Outputs

## JSON

Graphgenerator exports a json file containing information about the nodes (Twitter accounts, 'nodes') and the links between them ('edges'). 
them ('edges')

The file contains three types of information

### Edges

List of links between twitters that mention the hashtag (accounts that retweet or mention the tweet of another account). 
tweet of another account). For each link between accounts we have the following information: 
- source`: name of the twitter account that retweeted or mentioned another account
- `target`: the retweeted or mentioned account
- size`: the size of the link, i.e. the number of mentions or RTs from 'source' to 'target
- `label`:
- `id`: the id of the link
- type`:
- `metadata`: additional information about the link:
  - `date`: list of dates on which RTs or mentions occurred
  - quoted`: list of links of mentions, in order of dates
  - `RT`: list of RT links, by date order

### Nodes

List of twitter accounts that are mentioned or RT or mention or RT a tweet containing the hashtag 
searched. For each account, we have the following information:
- `id`: account id
- `label`: name of the twitter account
- `size`: size of the node, i.e. number of times i was RT'd or mentioned
- `from`: name of the account
- `community_id`: id of the community detected thanks to the community algorithm
- `x`: x coordinate on the graph
- `y`: y coordinate on the graph
- metadata`: additional information about the node:
  - `date`: date of RTs, mentions or tweets from the account
  - `tweets`: list of urls of its tweets in ascending date order
  - `RT`: list of urls of its RTs in ascending date order
  - `quoted`: list of urls of its mentions in ascending order of dates
  - `dates_edges`: list of dates of RTs and mentions of this account (if any)

### Metadata

The `metadata` field contains additional information about the search and the results of the search performed.
- keyword: keyword or hashtag used in the search
- since`: date until which the tweets were searched
- maxresults`: maximum number of results in the search
- minretweets`: minimum number of RTs in the search
- `last_collected_tweet`: id of the last collected tweets
- `last_collected_date`: date of the last collected tweet

## Graph

A png file can be exported using the `--img_path` command line option (or the 
export_img_graph()` method of `GraphBuilder`).
The file allows you to quickly visualize the shape of the graph and thus test different types of layout.


## Example layout

Using the following command in the terminal:
```commandline
graphgenerator "#boycottfrance" --layout_algo "layout_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png"
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

you  get the following results (code was run on 09/12/2021):

|      Spiral Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spiral.png "Spiral")       |          Spring Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spring.png "Spring")           |
|:-----------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------:|
| **Circular Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_circular.png "Circular") | **Kamada Kawai Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_kamada_kawai.png "Kamada Kawai") |
|      **Random Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_random.png "Random")      |                                                                                                         


## Example community detection 

Using the following code in the terminal (`"community_algo"` must be taken in  
`["greedy_modularity", "asyn_lpa_communities", "girvan_newman", "label_propagation", "louvain"]`) :
```commandline
graphgenerator "#boycottfrance" --layout_algo "spring" --community_algo "community_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png"
```
Depending on the algorithm you use, you will get the following resultats (the color indicates the community)

|         Girvan Newman <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_girvan_newman.png "Girvan Newmann")         | Greedy Modularity <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_greedy_modularity.png "Greedy modularity") |
|:--------------------------------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------:|
| **Label Propagation** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_label_propagation.png "Label Propagation") |             **Louvain** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_louvain.png "Louvain")              |


# Méthodologie

`Graphgenerator permet de recréer le réseau des interactions des comptes twitter sur un hashtag ou mot (ou groupe de mots) 
donné. 

## Collecte des tweets

Les données sont collectées par `Graphgenerator` en utilisant l'outil de collecte `snscrape`. Cet outil récolte les données
qui s'affichent lorsque l'on réalise une recherche dans barre de recherche de Twitter. Il ne permet de récupérer 
seulement les retweets des sept derniers jours (au delà seuls les tweets et mentions peuvent être collectés). La 
collecte est donc bornées au sept derniers jours.

`Graphgenerator` collecte tous les tweets qui sont des retweets ou mentions de tweets mentionnant le hashtag (ou mot ou 
groupe de mot) indiqué dans la recherche.

Sont seulement stockés les retweets et mentions dont le tweet source a été publié après la date du dernier retweet ou 
mention de tweet collectés. Cela permet de s'assurer que l'on dispose de tous les retweets d'un tweet donné. 

## Création du graph

Une fois les tweets collectés, ils sont réarrangés de manière à créer des liens entre les comptes twitter.
Deux comptes twitter sont liés si l'un mentionne ou retweet le tweet de l'autre. Un sens de direction est attaché 
au lien. Des poids sont alloués à chaque lien et corresponde au nombre d'occurence de ce lien (nombre totel de retweet et 
mentions d'un compte vers l'autre). 

Les données sont aussi aggrégées au niveau des comptes qui forment les noeuds du graph. La taille qui y est attribuée 
correspond au nombre total de tweets et de mentions de tweets émis par ce compte.

Les données sont mises au format de graph grâce à la bibliothèque `networkx`.

## Layout

Pour permettre la bonne visualisation du graph, des coordonnées dans un plan en 2D (ou 3D) sont attribuées à chaque 
noeuds.

Plusieurs algorithmes permettent de calculer les coordonnées des noeuds d'un graph pour le réprésenter au mieux. 
L'objectif est de résumer au mieux l'information dans le graph tout en la rendant lisible. 
Généralement les algorithmes tentent de minimiser le nombre d'intersections des liens (par considération esthétique, 
de lisibilité), de rapprocher les noeuds qui onet beaucoup de liens entre eux et de placer au centre du graph les noeuds
"centraux" (qui permettent de faire circuler l'information au sein du réseau).

`networkx` fournit de nombreuses possibilités de visualisations et une bonne partie sont disponibles dans Graphgenerator. 
Nous proposons d'utiliser par défaut l'aglorithme spring ou Fruchterman-Reingold (https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html).
Il fonctionne très bien avec de larges réseaux (ce qui est notre cas).

## Communautés

`Graphgenerator` permet également d'identifier des clusters. Ils correspondent à des groupes de comptes qui interagissent 
beaucoup entre eux. 

Encore une fois, `networkx` fournit un large choix d'algorithmes pour identifier ces communautés, qui sont pur la plupart 
disponibles dans `graphgenerator`. 

Par défaut, nous avons choisi un algorithme qui n'est pas disponible dans `networkx` mais dans une bibliothèque 
indépendante. Il repose sur la "méthode de louvain". Cette méthode est particulièrement efficace pour les gros réseaux.

#Sorties

## JSON

Graphgenerator exporte un fichier json contenant les informations sur les noeuds (comptes Twitter, 'nodes') et les liens entre 
eux ('edges')

Le fichier contient trois types d'informations

### Edges

Liste des liens entre les comptes twitters qui mentionnent le hashtag recherché (comptes qui retweete ou mentionne le 
tweet d'un autre compte). Pour chaque liens entre les comptes on dispose des informations suivantes: 
- `source`: nom du compte twitter qui a retweeté ou mentionné un autre compte
- `target`: le compte retweeté ou mentionné
- `size`: la taille du lien, i.e. le nombre de mention ou RT de 'source' vers 'target'
- `label`:
- `id`: l'id du lien
- `type`:
- `metadata`: information aditionnelles sur le lien:
  - `date`: liste des dates auxquelles ont eu lieu les RT ou mentions
  - `quoted`: liste des liens des mentions, par ordre ds dates
  - `RT`: liste des liens des RT, par ordre ds dates

### Nodes

Liste des comptes twitter qui sont mentionnés ou RT ou alors qui mentionnent ou RT un tweet contenant le hashtag 
recherché. POur chaque comptes, on dispose des informations suivantes:
- `id`: id du compte
- `label`: nom du compte twitter
- `size`: taille du noeud, i.e. nombre de fois où i la été RT ou mentionné
- `from`
- `community_id`: id du cluster détecté grâce à l'algo de communauté
- `x`: coordonnées x du noeud dans le graph
- `y`: coordonnées y du noeud dans le graph
- `metadata`: informations additionnelles sur le noeud:
  - `date`: date des RT, mentions ou tweets du compte
  - `tweets`: liste des urls de ses tweets par ordre croissant des dates
  - `RT`:  liste des urls de ses RT par ordre croissant des dates
  - `quoted`:  liste des urls de ses mentions par ordre croissant des dates
  - `dates_edges`: liste des dates des RT et mentions de ce compte (s'il y en a)

### Metadata

Le champs `metadata` contient des informations additionnelles sur la recherche et les résultats de al recherche effectuée.
- `keyword`: mot clé ou hashtag utilisé dans la recherche
- `since`: date jusqu'à laquelle les tweets ont été cherchés
- `maxresults`: nombre maximal de résultats dans la recherche
- `minretweets`: nombre de RT minimal dans la recherche
- `last_collected_tweet`: id du dernier tweets collecté
- `last_collected_date`: date du dernier tweet collecté

## Graph

Un fichier png peut être exporté en utilisant l'option `--img_graph` en ligne de commande (ou la méthode 
`export_img_graph()` de `GraphBuilder`).
Le fichier permet de visualiser rapidement la forme du graph et donc de tester différents types de 'layout'.



## Exemple layout

En utilisant le code suivant dans le terminal:
```commandline
graphgenerator "#boycottfrance" --layout_algo "layout_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png"
```
ou dans un script Python:
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
Vous obtiendrez les résultats suivants (le code a été executé le 09/12/2021):

|      Spiral Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spiral.png "Spiral")       |          Spring Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spring.png "Spring")           |
|:-----------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------:|
| **Circular Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_circular.png "Circular") | **Kamada Kawai Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_kamada_kawai.png "Kamada Kawai") |
|      **Random Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_random.png "Random")      |                                                                                                         

## Example détection de cluster

En utilisant le code suivant dans le terminal (`"community_algo"` doit être pris dans 
`["greedy_modularity", "asyn_lpa_communities", "girvan_newman", "label_propagation", "louvain"]`) :
```commandline
graphgenerator "#boycottfrance" --layout_algo "spring" --community_algo "community_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png"
```
Suivant l'algorithme utilisé, on obtient ces résultats (les couleurs indiques l'appartenance à une communauté)

|         Girvan Newman <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_girvan_newman.png "Girvan Newmann")         | Greedy Modularity <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_greedy_modularity.png "Greedy modularity") |
|:--------------------------------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------:|
| **Label Propagation** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_label_propagation.png "Label Propagation") |             **Louvain** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_louvain.png "Louvain")              |

