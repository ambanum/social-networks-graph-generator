[Read in english](./explanation.md)

# Méthodologie

Graphgenerator permet de recréer le réseau des interactions des comptes twitter sur un hashtag ou mot (ou groupe de mots) donné.

## Collecte des tweets

Les données sont collectées par Graphgenerator en utilisant l'outil de collecte [snscrape](https://github.com/JustAnotherArchivist/snscrape). Cet outil récolte les données qui s'affichent lorsque l'on réalise une recherche dans barre de recherche de Twitter. Il ne permet de récupérer seulement les retweets des **sept derniers jours** (au delà seuls les tweets et mentions peuvent être collectés).

Graphgenerator collecte tous les tweets qui sont des retweets ou mentions de tweets mentionnant le hashtag (ou mot ou groupe de mot) indiqué dans la recherche.

Sont seulement stockés les retweets et mentions dont le tweet source a été publié après la date du dernier retweet ou mention de tweet collectés. Cela permet de s'assurer que l'on dispose de tous les retweets d'un tweet donné.

Pendant la collecte, Graphgenerator calculera aussi un score de bot pour chaque utilisateur à l'aide de la librairie [botfinder](https://github.com/ambanum/social-networks-bot-finder).

## Création du graph

Une fois les tweets collectés, ils sont réarrangés de manière à créer des liens entre les comptes twitter. Deux comptes twitter sont liés si l'un mentionne ou retweet le tweet de l'autre. Un sens de direction est attaché au lien. Des poids sont alloués à chaque lien et corresponde au nombre d'occurence de ce lien (nombre totel de retweet et mentions d'un compte vers l'autre).

Les données sont aussi aggrégées au niveau des comptes qui forment les noeuds du graph. La taille qui y est attribuée correspond au nombre total de tweets et de mentions de tweets émis par ce compte.

Les données sont mises au format de graph grâce à la bibliothèque [Networkx](https://networkx.org/).

## Layout

Pour permettre la bonne visualisation du graph, des coordonnées dans un plan en 2D (ou 3D) sont attribuées à chaque noeuds.

Plusieurs algorithmes permettent de calculer les coordonnées des noeuds d'un graph pour le réprésenter au mieux. L'objectif est de résumer au mieux l'information dans le graph tout en la rendant lisible. Généralement les algorithmes tentent de minimiser le nombre d'intersections des liens (par considération esthétique, de lisibilité), de rapprocher les noeuds qui ont beaucoup de liens entre eux et de placer au centre du graph les noeuds "centraux" (qui permettent de faire circuler l'information au sein du réseau).

La commande `networkx` fournit de nombreuses possibilités de visualisations et une bonne partie sont disponibles dans Graphgenerator. Nous proposons d'utiliser par défaut l'algorithme spring ou [Fruchterman-Reingold](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html) parcequ'ils fonctionnent très bien avec de larges réseaux (ce qui est notre cas).

Les algorithmes de calcul du layout disponibles dans graphgenerator sont les suivants:
- Circular ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.circular_layout.html), [page Wikipédia](https://en.wikipedia.org/wiki/Circular_layout))
- Kamada Kawai ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html), [page Wikipédia](https://en.wikipedia.org/wiki/Force-directed_graph_drawing))
- Spring ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html))
- Random ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.random_layout.html), [page Wikipédia](https://fr.wikipedia.org/wiki/Graphe_al%C3%A9atoire))
- Spiral ([doc](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spiral_layout.html))

## Communautés

Graphgenerator permet également d'identifier des clusters. Ils correspondent à des groupes de comptes qui interagissent beaucoup entre eux.

Encore une fois, Networkx fournit un large choix d'algorithmes pour identifier ces communautés, qui sont pour la plupart disponibles dans Graphgenerator.

Par défaut, nous avons choisi un algorithme qui n'est pas disponible dans Networkx mais dans une bibliothèque indépendante. Il repose sur la "méthode de louvain". Cette méthode est particulièrement efficace pour les gros réseaux.

Les algorithmes de détection de communautés disponibles dans graphgenerator son les suivants:
- Greedy modularity ([doc](https://networkx.org/documentation/networkx-2.2/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html) )
- Asynchronous Label Propagation ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.label_propagation.asyn_lpa_communities.html))
- Girvan Newman ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.centrality.girvan_newman.html), [page Wikipédia](https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm))
- Label propagation ([doc](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.label_propagation.label_propagation_communities.html))
- Louvain ([doc](https://github.com/taynaud/python-louvain), [page Wikipédia](https://fr.wikipedia.org/wiki/M%C3%A9thode_de_Louvain))

## Enrichir un graph existant

En utilisant la commande `input_graph_json_path` de `graphgenerator`, vous pouvez enrichir un graph existant (une sortie au format `json` de `graphgenerator`). Les paramètres utilisés lors de sa création seront alors utilisés pour l'enrichir.

Le graph existant doit avoit été créé dans les septs jours précédents, sinon la commande ne fonctionnera pas (seul les retweets des 7 derniers jours sont accessibles).

## Export par batch

Si l'option `batch_size` est spécifiée et > 0 alors le graph est exporté tous les `batch_size` tweets collectés. Par défaut `batch_size` = 0, et dans ce cas le graph n'est exporté qu'une fois toutes les données collectées.

# Sorties

## JSON

Graphgenerator exporte un fichier json contenant les informations sur les noeuds (comptes Twitter, 'nodes') et les liens entre eux ('edges').

Le fichier contient trois types d'informations

### Edges

Liste des liens entre les comptes twitters qui mentionnent le hashtag recherché (comptes qui retweete ou mentionne le tweet d'un autre compte). Pour chaque liens entre les comptes on dispose des informations suivantes :

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

Liste des comptes twitter qui sont mentionnés ou RT ou alors qui mentionnent ou RT un tweet contenant le hashtag recherché. Pour chaque comptes, on dispose des informations suivantes :

- `id`: id du compte
- `label`: nom de l'utilisateur
- `size`: taille du noeud, i.e. nombre de fois où i la été RT ou mentionné
- `from`: nom de l'utilisateur
- `community_id`: id du cluster détecté grâce à l'algo de communauté
- `x`: coordonnées x du noeud dans le graph
- `y`: coordonnées y du noeud dans le graph
- `z`: coordonnées y du noeud dans le graph (si l'option 3D a été choisie)
- `metadata`: informations additionnelles sur le noeud:
  - `dates`: date des RT, mentions ou tweets du compte
  - `tweets`: liste des urls de ses tweets par ordre croissant des dates
  - `RT`: liste des urls de ses RT par ordre croissant des dates
  - `quoted`: liste des urls de ses mentions par ordre croissant des dates
  - `dates_edges`: liste des dates des RT et mentions de ce compte (s'il y en a)
  - `botscore`: probabilité que le compte soit un bot, calculé grâce à [botfinder](https://github.com/ambanum/social-networks-bot-finder)

### Metadata

Le champs `metadata` contient des informations additionnelles sur la recherche et les résultats de la recherche effectuée.

- `keyword`: mot clé ou hashtag utilisé dans la recherche
- `since`: date jusqu'à laquelle les tweets ont été cherchés
- `maxresults`: nombre maximal de résultats dans la recherche
- `minretweets`: nombre de RT minimal dans la recherche
- `last_collected_tweet`: id du dernier tweets collecté
- `last_collected_date`: date du dernier tweet collecté
- `data_collection_date`: date de la data collection
- `most_recent_tweet`: tweet id du premier tweet collecté
- `execution_time`: temps d'execution du code
- `layout_algo`: algorithme de layout utilisé
- `community_algo`: algorithme de détection des communautés utilisé
- `n_collected_tweets`: nombre de tweets collectés (utilisés pour la construction du graph)
- `n_analyzed_tweet`: nombre de tweets analysés
- `status`: status de la collecte donnée (peut être encore en cours si l'option`batch_size` est utilisée)

## Graph

Un fichier png peut être exporté en utilisant l'option `--img_graph` en ligne de commande (ou la méthode `export_img_graph()` de `GraphBuilder`). Le fichier permet de visualiser rapidement la forme du graph et donc de tester différents types de 'layout'.

## Exemple layout

En utilisant le code suivant dans le terminal:

```commandline
graphgenerator "#boycottfrance" --layout_algo "layout_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png" --compute_botscore
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

|      Spiral Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spiral.png "Spiral")       |            Spring Layout <br/>![alt](./img/%23boycottfrance_20211209_graph_spring.png "Spring")             |
| :---------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------: |
| **Circular Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_circular.png "Circular") | **Kamada Kawai Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_kamada_kawai.png "Kamada Kawai") |
|    **Random Layout** <br/> ![alt](./img/%23boycottfrance_20211209_graph_random.png "Random")    |

## Example détection de cluster

En utilisant le code suivant dans le terminal (`"community_algo"` doit être pris dans
`["greedy_modularity", "asyn_lpa_communities", "girvan_newman", "label_propagation", "louvain"]`) :

```commandline
graphgenerator "#boycottfrance" --layout_algo "spring" --community_algo "community_algo" --since "2021-12-02" --minretweets 1 --maxresults 1000 --img_path "graph.png"
```

Suivant l'algorithme utilisé, on obtient ces résultats (les couleurs indiques l'appartenance à une communauté)

|         Girvan Newman <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_girvan_newman.png "Girvan Newmann")         | Greedy Modularity <br/>![alt](./img/%23boycottfrance_20211209_graph_spring_greedy_modularity.png "Greedy modularity") |
| :------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------: |
| **Label Propagation** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_label_propagation.png "Label Propagation") |             **Louvain** <br/> ![alt](./img/%23boycottfrance_20211209_graph_spring_louvain.png "Louvain")              |
