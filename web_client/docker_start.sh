#!/bin/bash

cd /web_client
cp /config/main.json public/configs

/usr/bin/ember serve
