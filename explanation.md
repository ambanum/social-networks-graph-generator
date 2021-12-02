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