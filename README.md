<img src="https://disinfo.quaidorsay.fr/assets/img/logo.png" width="140">

# social-networks-graph-generator

A graph generator to visualise links between twitter accounts for a specific keyword or hashtag.

See our [methodology](./explanation.md) for graph generation.

## Install for common usage with pip

Create a virtual env if needed

```
pip3 install virtualenv
virtualenv -p python3 social-networks-graph-generator
source social-networks-graph-generator/bin/activate
```

Install

```
pip3 install social-networks-graph-generator
```

Then you can launch `graphgenerator`

## Install for development

```
git clone https://github.com/ambanum/social-networks-graph-generator
cd social-networks-graph-generator
```

### Virtual env

We strongly recommend that you use a virtual env for any development in python

For this

```
pip3 install virtualenv
virtualenv -p python3 social-networks-graph-generator
source social-networks-graph-generator/bin/activate
```

### build on local

If you do not want to develop but just use the software, do

```
./build.sh
```

Then you can use `graphgenerator` as an executable command

### use for development with no build

```
pip3 install -r requirements.txt
```

Then you can use `./graphgenerator-dev.py` as an executable command

# Usage

To get the graph of a keyword or hashtag, you can do so (using cli command)

```
# by search: this will use snscrape to get the data
graphgenerator "#hashtag"
graphgenerator "#hashtag" --maxresults=1000 --minretweets=1  --algo="spring" --json_path="output.json" --compute_botscore --batch_size=1000

# if you want to visualise the graph, you can choose to export a png file of it 
graphgenerator "#hashtag" --maxresults=1000 --minretweets=1 --algo="spring" --json_path="output.json" --img_path="graph.png"
```
Update an existing graph (it will update with data from the 7 past days)
```
# updating an existing graph (created using graphgenerator)
graphgenerator --input_graph_json_path=="input_from_graphgenerator.json"
```
Create a graph from snscrape output
```
# download twitter data using snscrape
snscrape --jsonl twitter-search "your_search" > "snscrape_output.json"
# create graph from this data
graphgenerator snscrape_json_path=="snscrape_output.json"

#it can also be combined with an existing graph if the last tweet of the collected data from snscrape was posted before the most recent tweet of the existing graph
graphgenerator --input_graph_json_path=="input_from_graphgenerator.json" snscrape_json_path=="snscrape_output.json" 

```

If using the option `snscrape_json_path` then the file used as an input for data should be in JSON Lines text format. Each line should contain a dictionary representing a tweet in a snscrape tweet format. Thus, it must contains the following fields:
- "user" (User class from snscrape)
- "date"
- "url"
- "id"
- "retweetedTweet" (Tweet class from snscrape, thus it must contains the above fields)
- "quotedTweet" (Tweet class from snscrape, thus it must contains the above fields)

Or you can choose to load graphgenerator as a library and use GraphBuilder class directly in your Python script

```
#import library 
from graphgenerator import GraphBuilder
# initialize Graph builder class
GB = GraphBuilder(
    search="#hashtag", 
    minretweets=1, 
    since="2021-12-05", 
    maxresults=None
)

# collect tweets, here we collect retweet and quotes of tweets mentionning "#hashtag" since "2021-12-05" (collect can only back max to 7 days)
NB.collect_tweets()
# or use NB.collect_tweets(snscrape_json_path="snscrape_output.json") to use data from snscrape output

# create node and edges pandas dataframe (NB.nodes and NB.edges) 
NB.clean_nodes_edges()
#or NB.clean_nodes_edges(input_json=input_json) if you want to update an existing graph saved in input_json

# create graph object (networkx format, stored in NB.G) and calculate position of the nodes using layout_algo)
NB.create_graph(layout_algo="spring")

# look for communities in the graph using community_algo
NB.find_communities(community_algo)

#export an image of the graph (this part is optionnal)
NB.export_img_graph(graph_path)

# export graph in a json format containing information about nodes and edges
NB.export_json_output(output_path)
```


You can also enrich an existing graph (created thanks to the `graphgenerator` command) as follows:

```commandline
graphgenerator --input_graph_json_path="path_to_input_json"
```

Same arguments as used when generating the input graph will then be used to enrich it. The command will be run only if 
input graph data were collected in the last 7 days.

## Example

```
 graphgenerator "ambnum" --maxresults 10 --compute_botscore
```

will return

```json
{
    "edges":
    [
        {
            "source": "AmbNum",
            "target": "MPubliques",
            "size": 1,
            "label": "has RT",
            "id": "edge_0",
            "type": "arrow",
            "metadata":
            {
                "date": ["2021-12-02 09:32:09+00:00"],
                "quoted": [""],
                "RT": ["https://twitter.com/AmbNum/status/1466339393812193283"]
            }
        },
        ...
    ],
    "nodes":
    [
        {
            "id": "AmbNum",
            "label": "@AmbNum",
            "size": 0.0,
            "from": "has RT",
            "metadata":
            {
                "date": ["2021-12-01 16:24:47+00:00", "2021-12-02 09:32:09+00:00"],
                "tweets": ["", ""],
                "quoted": ["", ""],
                "RT": ["https://twitter.com/AmbNum/status/1466080848147529731", "https://twitter.com/AmbNum/status/1466339393812193283"],
                "dates_edges": [],
                "botscore": 0.101
            },
            "x": 0.9420867798959837,
            "y": -0.3153417838051506,
            "community_id": 1
        },
        ...
    ],
    "metadata":
    {
        "search": "ambnum",
        "since": "2021-11-29",
        "type_search": "include:nativeretweets",
        "maxresults": 10,
        "minretweets": 1,
        "last_collected_tweet": 1465613154193399813,
        "last_collected_date": "2021-11-30 09:26:20+00:00",
        "data_collection_date": "2021-12-14 17:20:29.750030+00:00",
        "most_recent_tweet": "1470805898817949699"
      
    }
}
```

## Using Docker

### "regular" image

```sh
# build and run image yourself
docker build --tag graphgenerator:latest -f Dockerfile .
docker run -it -d --rm graphgenerator

# or pull from Dockerhub
#TODO

# execute your command in the container
docker exec -it graphgenerator graphgenerator --search ambnum
```

### ARM/M1 image (using conda)

Note that you need to activate the conda env everytime you want to use `docker exec` which slows things down... See [this article](https://pythonspeed.com/articles/activate-conda-dockerfile) for a description of the issue.

```sh
# build and run image yourself
docker build  --tag graphgenerator:latest -f Dockerfile.conda .
docker run -it -d --name graphgenerator --rm graphgenerator:latest

# execute your command in the container
docker exec -it graphgenerator conda init bash && conda activate graphgenerator && graphgenerator --search ambnum
```

# Deployment

This package is deployed on pypi as a package named `social-networks-graph-generator`. So that it can be installed using pip
We are using `twine` for this

```
pip install twine
npm install -g semver # for consistent package number generation
pip install gitchangelog # to generate changelog automatically based on git commits
```

## Authentication on pyPi

In order to not set your username and password again and again, you can set them using thos

```
keyring set https://upload.pypi.org/legacy/ username
```

## Deploy a new release

A new release should come with a new version
We are using semver to generate consistent package number

```
./release.sh
# org
./release.sh patch # for small fixes
./release.sh minor # for minor features
./release.sh major # for breaking changes
```

This will bum the version in `graphgenerator/version.py` and create a git tag

# Troubleshooting

## Illegal instruction: 4

If your installation fail, it might be because you're not using a virtual environment :

```
pip3 install virtualenv
virtualenv -p python3 social-networks-graph-generator
source social-networks-graph-generator/bin/activate
./build.sh
```

## ERROR: Could not detect requirement name...

```
ERROR: Could not detect requirement name for 'git+https://github.com/JustAnotherArchivist/snscrape.git', please specify one with #egg=your_package_name
```

In requirements.txt file, you have to add `#egg=your_package_name` to github repository url.
In this case, replace `git+https://github.com/JustAnotherArchivist/snscrape.git`by `git+https://github.com/JustAnotherArchivist/snscrape.git#egg=snscrape`

## Install on M1/ARM processors

As of today, the easiest way to install the package and its dependencies on a M1/ARM chip is via [`conda`](https://conda.io/)

#### Install `conda`

We recommend [downloading and installing](https://docs.conda.io/en/latest/miniconda.html#installing) the python 3.9 version of conda. The `miniconda` distribution is enough for our purpose.

#### Navigate to root of repository and pull the latest changes

#### Create a new conda environment

`conda env create --name graphgenerator python=3.9 -f environment.yml`

and activate it :

`conda activate graphgenerator`

#### Install graphgenerator

`python -m pip install -e .`

#### Check that it worked

```sh
graphgenerator --help
```
