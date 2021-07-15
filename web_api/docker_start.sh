#!/bin/bash

if [“$REFRESH_INTERNAL_DB” -eq “true”]; then
    echo "Refreshing the writeable Oil Database from noaa-oil-data"
    cd /adios-db/noaa-oil-data/
    adios_db_restore --config /config/config_oil_db.ini
    cd -
elif [“$MONGODB_WRITEABLE” -eq “true”]; then
    echo "Oil Database is writeable"

    echo "Backing up the database to noaa-oil-data"
    cd /adios-db/noaa-oil-data/
    adios_db_backup --config /config/config_oil_db.ini
    git status
    cd -
else
    echo "MongoDB is read-only"

    echo "Loading the database from noaa-oil-data"
    cd /adios-db/noaa-oil-data/
    adios_db_restore --config /config/config_oil_db.ini
    cd -
fi

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini
