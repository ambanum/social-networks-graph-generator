#!/bin/sh

# remove generated files
rm -Rf .eggs
rm -Rf *.egg-info
rm -Rf dist
rm -Rf build
rm -Rf __pycache__

NEW_VERSION_TYPE=$1

source social-networks-graph-generator/bin/activate
if [ -z $1 ]; then
    read -p 'version (patch|minor|major): ' NEW_VERSION_TYPE
fi

if [[ ! "$NEW_VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "$NEW_VERSION_TYPE shoud be patch|minor|major"
    exit 1
fi

CURRENT_VERSION=$(./graphgenerator-dev.py -v)
NEW_VERSION=$(semver $CURRENT_VERSION -i $NEW_VERSION_TYPE)

if [[ ! "$CURRENT_VERSION" ]]; then
    echo "CURRENT_VERSION does not exist"
    exit 1
fi

echo "Bumping from $CURRENT_VERSION to $NEW_VERSION"
# ".bak" is here for MacOS purpose, if we remove it does not work anymore
sed -i ".bak" "s/$CURRENT_VERSION/$NEW_VERSION/g" "graphgenerator/version.py"
git add graphgenerator/version.py
git commit -m "Version $NEW_VERSION"
git tag -a v$NEW_VERSION -m "Version $NEW_VERSION"

# update changelog
gitchangelog > CHANGELOG.md
git add CHANGELOG.md
git commit --amend -m "Version $NEW_VERSION"

python setup.py sdist bdist_wheel
twine upload dist/*