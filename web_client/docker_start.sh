#!/bin/bash

cd /web_client
cp /config/main.json public/configs

ember serve
