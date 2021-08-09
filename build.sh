#!/bin/sh

# remove generated files
rm -Rf .eggs
rm -Rf *.egg-info
rm -Rf dist
rm -Rf build
rm -Rf __pycache__

# initiate virtual environment
virtualenv -p python3 social-networks-graph-generator
source social-networks-graph-generator/bin/activate

# install requirements
pip3 install -r requirements.txt

# install command line
pip3 install .

# Launch command to show it worked and how to use
echo " "
echo " "
echo " "
echo " "
echo " "
graphgenerator