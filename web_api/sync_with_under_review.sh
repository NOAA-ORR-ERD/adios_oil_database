#!/bin/bash

# Script to sync active server with under_review branch

echo "Inside Script: $0"
set -e  # exit script if any commands fail
set -x  # echo commands to stdout

SCRIPT_DIR=$( cd -- "$( dirname -- "${0}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/git_functions.sh

cd /data/git_repos/noaa-oil-data/

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"

# To start, let's get our repo in a consistent state with our remote.
# First, we will update the local list of remote branches, as they may change
# when a merge request removes a branch and squashes commits.
git remote update origin --prune
git status

# The production branch is expected to always be present on the remote.
git checkout production
git pull -s recursive -X theirs --no-edit

# sync with the latest version on the server
if [[ $(branch_exists_remotely under_review) -eq "0" ]];
then
    echo "The remote under_review branch exists.  Check it out and pull."
    git checkout under_review
    git pull -s recursive -X theirs --no-edit
else
    echo "The remote under_review branch does not exist."
    echo "Checkout a local branch.  If it doesn't exist locally, create it."
    git checkout -b under_review
fi

# backup the data in the database

# commit the changes made in the server:
adios_db_backup --config /config/config_oil_db.ini
git add -A

if ! git diff-index --quiet HEAD --
then
    # changes made
    git commit -a -m "Save from Running Editable Server"

    # just in case something just changed outside of the pipeline
    git pull -s recursive -X theirs --no-edit

    git push origin under_review
else
    # just in case something just changed outside of the pipeline
    git pull -s recursive -X theirs --no-edit
fi


# update database with latest under_review branch
adios_db_restore --config /config/config_oil_db.ini
echo "Database is ready to be edited ..."
