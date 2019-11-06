#!/bin/bash

mongod --config /etc/mongod.conf &

/opt/conda/bin/pserve /config/config.ini
