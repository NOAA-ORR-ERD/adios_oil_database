#!/bin/bash

echo $(pwd)
ls -la

echo "Starting our server on host:port:"
egrep -w "host|port" /config/config.ini

/opt/conda/bin/pserve /config/config.ini CAN_MODIFY_DB=${CAN_MODIFY_DB:-false}
