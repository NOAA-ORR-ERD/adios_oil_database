#!/bin/bash

echo `pwd`

./web_api/docker_backup_db.sh

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini
