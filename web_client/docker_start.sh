#!/bin/bash

cd /web_client
cp /config/main.json public/configs

ls -l /usr/bin

/usr/bin/ember serve
