#!/bin/bash

if [ “$REFRESH_INTERNAL_DB” == “true” ]; then
    echo "Refreshing the writeable Oil Database from noaa-oil-data"
    cd /noaa-oil-data/

    git checkout -b under_review
    git pull origin under_review

    adios_db_restore --config /config/config_oil_db.ini
    cd -
elif [ “$MONGODB_WRITEABLE” == “true” ]; then
    echo "Oil Database is writeable"
    cd /noaa-oil-data/

    git config --global user.email "adios-script@noaa.gov"
    git config --global user.name "Adios Automated Script"

    # make sure both of our repo branches are current
    echo ">>> checkout & pull production branch"
    git checkout production
    git pull

    echo ">>> checkout & pull under_review branch"
    git remote set-branches origin under_review
    git fetch origin under_review
    git checkout under_review
    git pull

    echo ">>> Backing up the database to noaa-oil-data"
    adios_db_backup --config /config/config_oil_db.ini

    echo ">>> Stage our changes"
    git add --all

    echo ">>> Perform a commit only if there are changes"
    git diff-index --quiet HEAD || git commit -m "Archiving changes to under_review from pipeline"

    echo ">>> Git status"
    git status

    echo ">>> pushing under_review branch"
    git push origin under_review

    # This should incorporate any changes in the production branch that have
    # been made outside the scope of the under_review branch, so they will be
    # seen as changes in the under_review branch history.
    echo ">>> rebase production under_review"
    git rebase production under_review

    echo ">>> Refresh the database with new baseline"
    adios_db_restore --config /config/config_oil_db.ini

    cd -
else
    echo "MongoDB is read-only"

    echo "Loading the database from noaa-oil-data"
    cd /noaa-oil-data/
    adios_db_restore --config /config/config_oil_db.ini
    cd -
fi

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini
