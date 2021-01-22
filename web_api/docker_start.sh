#!/bin/bash

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini
