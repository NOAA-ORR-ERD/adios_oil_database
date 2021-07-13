#!/bin/bash

if $MONGODB_WRITEABLE
then 
    echo "MongoDB is writeable"
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
