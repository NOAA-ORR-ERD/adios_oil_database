#!/bin/bash

# Script to backup oil database and set it to production branch

echo "Inside Script: $0"
set -e  # exit script if any commands fail
set -x  # echo commands to stdout

SCRIPT_DIR=$( cd -- "$( dirname -- "${0}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/git_functions.sh

cd /data/git_repos/noaa-oil-data/

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"


# this will update the local list of remote branches, as they may change
# when a merge request removes a branch and squashes commits.
git remote update origin --prune

git status

if [[ $(branch_exists_remotely under_review) -eq "0" ]];
then
    echo "The remote under_review branch exists."
    BRANCH=under_review
else
    echo "The remote under_review branch does not exist.  Use a side branch."
    BRANCH=`date +'%Y/%m/%d_%H;%M'`
fi

git checkout production
git pull -s recursive -X theirs --no-edit

# The local under_review branch might be in a different state as the remote
# This might happen if a merge request on GitLab removes a branch and
# squashes commits.  So we remove the local under_review branch
git branch -D under_review || echo "local under_review not found. This is ok."

git checkout -b $BRANCH

# Save out what's in the mongodb
adios_db_backup --config /config/config_oil_db.ini
git add -A

if ! git diff-index --quiet HEAD --
then
    # changes made in the MongoDB will be saved in the branch that we
    # decided on.
    git commit -a -m "Save from Running Editable Server"
    git push --set-upstream origin $BRANCH
fi

# Update the MongoDB with the GitLab's current production branch
git checkout production
git pull
adios_db_restore --config /config/config_oil_db.ini
echo "Database is ready to be edited ..."

# Since we are syncing with the production branch, the the under_review branch
# changes will be dropped
git branch -D under_review
git push origin --delete under_review

# create a new clean under_review branch
git checkout production
git checkout -b under_review
git push --set-upstream origin under_review

if [[ "$BRANCH" != "under_review" ]];
then
    echo "cleaning up the side-branch $BRANCH"
    git branch -D $BRANCH  # clean up our local branch
fi
