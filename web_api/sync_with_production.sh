#!/bin/bash

# Script to backup oil database and set it to production branch
echo "In sync_with_production.sh script"

set -e  # exit script if any commands fail
set -x  # echo commands to stdout

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


cd /data/git_repos/noaa-oil-data/

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"

git status

# backup the data in the database

BRANCH=`date +'%Y/%m/%d_%H;%M'`

# this will update the local list of remote branches
git remote update origin --prune


# The local under_review branch might be in a different state as the remote
# This might happen if a merge request removes a branch and squashes commits.
git checkout production
git pull

git branch -D under_review

if [[ $(branch_exists_remotely under_review) -eq "0" ]]
then
    echo "The remote under_review branch exists."
    git checkout under_review
else
    echo "The remote under_review branch does not exist.  Use production."
fi

git checkout -b $BRANCH

# Save out what's in the mongodb
adios_db_backup --config /config/config_oil_db.ini
git add -A

if ! git diff-index --quiet HEAD --
then
    # changes made
    git commit -a -m "Save from Running Editable Server"
    git push --set-upstream origin $BRANCH
fi

# update database with latest production
git checkout production
git pull
adios_db_restore --config /config/config_oil_db.ini
echo "Database is ready to be edited ..."

# delete the under_review branch
git branch -D under_review
git push origin --delete under_review

# create a new clean under_review branch
git checkout production
git checkout -b under_review
git push --set-upstream origin under_review

git branch -D $BRANCH  # clean up our local branch
