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
import sys
from subprocess import run, Popen
import atexit
import time
import urllib.request
import webbrowser

rebuild = True if "--rebuild" in sys.argv else False


# start up mongo:

mongo = Popen(['mongod', '-f', 'mongo_config_dev.yml'])

# print("after starting mongo")

webapi = Popen(['pserve', '--reload', 'web_api/config-example.ini'])

# print("after starting the webapi")

os.chdir('web_client')

if rebuild:
    # make sure npm packages are up to date
    print("Updating/installing npm packages")
    run(["npm", "install"])
    print("Done with npm packages")

print("Starting up Ember Serve")
client = Popen(['ember', 'serve'])

print("after starting up the client")

pids = [os.getpid()] + [p.pid for p in (mongo, webapi, client)]

os.chdir('..')

print(os.getcwd())
monitor = Popen(['python', 'utilities/monitor_and_kill.py'] +
                [str(pid) for pid in pids])


def wait_for_client_server():
    while True:
        try:
            urllib.request.urlopen("http://localhost:4200/")
        except urllib.request.URLError:
            print("waiting for ember server to start up")
            time.sleep(1.0)
            continue


def kill_everything():
    print("killing everything on exit")
    mongo.terminate()
    webapi.terminate()
    client.terminate()
    # should we kill the monitor here? it should kill itself


atexit.register(kill_everything)

wait_for_client_server()
webbrowser.open('http://localhost:4200/', new=1)

while True:
    print("App running: http://localhost:4200/")
    print("Hit ^C To stop:")
    time.sleep(2.0)

