#!/bin/bash

# Script to initialize the noaa-oil-data Git repository on the writable
# adios database server
echo "In: init_noaa_data.sh script"

set -e  # exit script if any commands fail
set -x  # echo commands to stdout

SCRIPT_DIR=$( cd -- "$( dirname -- "${0}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/git_functions.sh

REPO_NAME=noaa-oil-data

cd /data/git_repos

if [ -d $REPO_NAME ]
then
    echo "$REPO_NAME exists. Dropping the repository."
    rm -rf $REPO_NAME
fi

echo "Cloning the repo"
git clone ssh://git@gitlab.orr.noaa.gov:9933/gnome/oil_database/$REPO_NAME.git $REPO_NAME

cd $REPO_NAME

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"

git status

# setup the initial state of the repository
if [ $(branch_exists under_review) ]
then
    echo "The under_review branch already exists."
    git checkout under_review
else
    echo "Creating the under_review branch."
    git checkout production
    git checkout -b under_review
    git push --set-upstream origin
fi


echo "The $REPO_NAME repository has been initialized ..."
