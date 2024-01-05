#!/bin/bash
# Script to restore the local Mongo DB with the remote under_review branch
# of the noaa-oil-data Git repo.
# We will **NOT** try to save any local MongoDB changes.
#
# 1 - Get our repo in a consistent state with our remote.  (always)
# 2 - Pull the remote production branch changes (should always exist).
# 3 - If the remote under_review branch exists:
#     3a - Pull the remote under_review branch changes.
# 3 - Else:
#     - If the local under_review branch exists:
#         3b - Remove the local branch  (No local changes, remote changes only)
#     3c - Create the under_review branch locally.
#     3d - Push it out to the remote.
# 4 - Restore the Mongo DB from the under_review branch.

echo "Inside Script: $0"
set -e  # exit script if any commands fail
set -x  # echo commands to stdout

SCRIPT_DIR=$( cd -- "$( dirname -- "${0}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/git_functions.sh

cd /data/git_repos/noaa-oil-data/

git config user.email "adios-script@noaa.gov"
git config user.name "Adios Automated Script"

# 1. To start, let's get our repo in a consistent state with our remote.
# First, we will update the local list of remote branches, as they may change
# when a merge request removes a branch and squashes commits.
git remote update origin --prune
git status

# 2. Pull the remote production branch.
git checkout production
git pull -s recursive -X theirs --no-edit

# sync with the latest version on the server
if [[ $(branch_exists_remotely under_review) -eq "0" ]];
then
    echo "The remote under_review branch exists.  Check it out and pull."
    # 3a. Pull the remote under_review branch changes.
    git checkout under_review
    git pull -s recursive -X theirs --no-edit
else
    echo "The remote under_review branch does not exist."
    if [[ $(branch_exists_locally under_review) -eq "0" ]];
    then
        echo "The local under_review branch exists."
        # 3b. Remove the local under_review branch.
        git branch -D under_review
    fi
    # 3c. Create the local under_review branch.
    git checkout -b under_review
    # 3d. Push it to the remote.
    git push --set-upstream origin under_review
fi

# 4 - Restore the Mongo DB with the latest under_review branch
adios_db_restore --config /config/config_oil_db.ini
echo "Database is ready to be edited ..."
