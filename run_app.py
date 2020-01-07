#!/usr/bin/env python

"""
Script to start up the application for development

This assumes you have an initialized DB already
 (I should probably make that an option)


In Python, so it has some hope of working cross platform


But only tested on OS-X -- if you get it working on Windows,
please update this note (and the script itself)

There should probably be something here to update the conda
environment and all that. but for now, just starting it up.

"""
import os
from subprocess import run, Popen
import atexit
import time
import webbrowser

# start up mongo:

mongo = Popen(['mongod', '-f', 'mongo_config_dev.yml'])

# print("after starting mongo")

webapi = Popen(['pserve', '--reload', 'web_api/config-example.ini'])

# print("after starting the webapi")

os.chdir('web_client')
client = Popen(['ember', 'serve'])

print("after starting up the client")



def kill_everything():
    print("killing everything on exit")
    mongo.terminate()
    webapi.terminate()


atexit.register(kill_everything)

webbrowser.open('http://localhost:4200/', new=1)

while True:
    print("App running: http://localhost:4200/")
    print("Hit ^C To stop:")
    time.sleep(2.0)





