#!/bin/bash

redis-server --daemonize yes

mongod --config /etc/mongod.conf &

/opt/conda/bin/pserve /config/config.ini
