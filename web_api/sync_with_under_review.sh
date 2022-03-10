#!/bin/bash

# Script to sync active server with under_review branch
echo "In: sync_with_under_review.sh script"

#set -e  # exit script if any commands fail
set -x  # echo commands to stdout

cd /data/git_repos/noaa-oil-data/

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"

git status

# backup the data in the database

# this will update the local list of remote branches, as they may change
# when a merge request removes a branch and squashes commits.
git remote update origin --prune

# sync with the latest version on the server
git checkout under_review
git pull -s recursive -X theirs --no-edit

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
