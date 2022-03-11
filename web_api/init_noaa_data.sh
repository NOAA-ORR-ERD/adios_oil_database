#!/bin/bash

# Script to initialize the noaa-oil-data Git repository on the writable
# adios database server
echo "In: init_noaa_data.sh script"

set -e  # exit script if any commands fail
set -x  # echo commands to stdout

REPO_NAME=noaa-oil-data

function branch_exists_locally() {
    local branch=${1}
    local exists_in_local=$(git branch --list ${branch})

    if [[ -n ${exists_in_local} ]]
    then
        echo 0
    else
        echo 1
    fi
}

function branch_exists_remotely() {
    local branch=${1}
    local exists_in_remote=$(git ls-remote --heads origin ${branch})

    if [[ -n ${exists_in_remote} ]]
    then
        echo 0
    else
        echo 1
    fi
}

function branch_exists() {
    local branch=${1}
    local exists_in_local=$(git branch --list ${branch})
    local exists_in_remote=$(git ls-remote --heads origin ${branch})

    if [[ -n ${exists_in_local} ]] || [[ -n ${exists_in_remote} ]]
    then
        echo 0
    else
        echo 1
    fi
}


cd /data/git_repos

if [ -d $REPO_NAME ]
then
    echo "$REPO_NAME exists. Dropping the repository."
    rm -rf $REPO_NAME
fi

echo "Cloning the repo"
git clone ssh://git@gitlab.orr.noaa.gov:9933/gnome/oil_database/$REPO_NAME-test.git $REPO_NAME

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
