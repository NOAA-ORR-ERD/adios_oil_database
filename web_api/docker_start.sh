#!/bin/bash

REPO_NAME=noaa-oil-data-test
git config --global user.email "adios-script@noaa.gov"
git config --global user.name "Adios Automated Script"


# clone the repo
# this may be done in the docker build, but for now, for testing ...
echo "Cloning the repo"
git clone --depth 1 ssh://git@gitlab.orr.noaa.gov:9933/gnome/oil_database/$REPO_NAME.git /$REPO_NAME/


if [ “$REFRESH_INTERNAL_DB” == “true” ]; then
    echo "Refreshing the writeable Oil Database from noaa-oil-data"
    cd /$REPO_NAME/

    git checkout production
    git pull origin production

    # get set up to do new edits
    # delete the old working copy
    echo ">>> git branch -D server_working_copy"
    git branch -D server_working_copy
    echo ">>> git push origin --delete working_copy"
    git push origin --delete server_working_copy

    # make a new working copy of production branch to work from
    echo ">>> git checkout -b server_working_copy"
    git checkout -b server_working_copy

    # save it on the gitlab server so we can retrieve it at the next deploy
    echo ">>> git push --set-upstream origin server_working_copy"
    git push --set-upstream origin server_working_copy

    echo "Loading database with the production copy"
    adios_db_restore --config /config/config_oil_db.ini

    cd -

elif [ “$MONGODB_WRITEABLE” == “true” ]; then
    echo "Oil Database is writeable"

    cd /$REPO_NAME/

    # getting the branches we need in
    echo ">>> git remote set-branches --add origin under_review"
    git remote set-branches --add origin under_review
    echo ">>> git remote set-branches --add origin server_working_copy"
    git remote set-branches --add origin server_working_copy
    echo ">>> git fetch origin"
    git fetch origin

    echo ">>> git checkout server_working_copy"
    git checkout server_working_copy # get back where we were.

    echo "Saving the contents of the database to the working copy"
    echo ">>> adios_db_backup --config /config/config_oil_db.ini"
    adios_db_backup --config /config/config_oil_db.ini

    echo ">>> git add -A"
    git add -A

    echo ">>> git commit -m "changes made in Web UI""
    git commit -m "changes made in Web UI"


    # Get the latest under_review branch
    echo ">>> git checkout under_review"
    git checkout under_review

    echo ">>> git pull"
    git pull

    git checkout production -- validation/validation_by*

    # get the under_review branch in sync with production
    echo ">>> git merge production"
    git merge -m "merging changes from production into under_review" production

    git checkout server_working_copy -- validation/validation_by*

    # merge the changes from the server into under_review branch
    echo ">>> git merge server_working_copy"
    git merge -m "merging changes from server into under_review" server_working_copy

    # push changes in under_review back to server.
    echo ">>> git push"
    git push


    # get set up to do new edits
    # delete the old working copy -- those changes have been merged into under_review
    echo ">>> git branch -D server_working_copy"
    git branch -D server_working_copy
    echo ">>> git push origin --delete working_copy"
    git push origin --delete server_working_copy

    # make a new working copy of the under_review branch to work from
    echo ">>> git checkout -b server_working_copy"
    git checkout -b server_working_copy

    # save it on the gitlab server so we can retrieve it at the next deploy
    echo ">>> git push --set-upstream origin server_working_copy"
    git push --set-upstream origin server_working_copy

    # 3 d) reload the database including any changes merged from production, etc.
    echo "Reloading new data to the database"
    echo ">>> adios_db_restore"
    adios_db_restore --config /config/config_oil_db.ini

    echo "Database is ready to be edited ..."
    # DONE -- the server is now running

    cd -
else
    echo "MongoDB is read-only"

    echo "Loading the database from noaa-oil-data"
    cd /$REPO_NAME/
    git checkout production
    git pull
    adios_db_restore --config /config/config_oil_db.ini
    cd -
fi

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini
