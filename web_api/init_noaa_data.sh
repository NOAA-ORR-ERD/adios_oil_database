#!/bin/bash

# Script to initialize the noaa-oil-data Git repository on the writable
# adios database server
echo "In: init_noaa_data.sh script"

BRANCH_NAME=${BRANCH_NAME:-"under_review"}

set -e # exit script if any commands fail
set -x # echo commands to stdout

SCRIPT_DIR=$(cd -- "$(dirname -- "${0}")" &>/dev/null && pwd)
source ${SCRIPT_DIR}/git_functions.sh

REPO_NAME=noaa-oil-data

if [ -d /$REPO_NAME ]; then
    echo "/$REPO_NAME exists. Dropping the repository."
    rm -rf /$REPO_NAME
fi

echo "Cloning the repo"
git clone https://adios-api:${noaa_oil_data_token}@gitlab.orr.noaa.gov/gnome/oil_database/noaa-oil-data.git /$REPO_NAME

cd $REPO_NAME

# setup the initial state of the repository
if [ $(branch_exists $BRANCH_NAME) ]; then
    echo "The $BRANCH_NAME branch already exists."
    git checkout $BRANCH_NAME
else
    echo "Creating the $BRANCH_NAME branch."
    git checkout production
    git checkout -b $BRANCH_NAME
    git push --set-upstream origin
fi

echo "The $REPO_NAME repository has been initialized ..."
