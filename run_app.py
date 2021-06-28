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
import urllib.request
import webbrowser
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--rebuild", '-r',
                    action="store_true",
                    help='Rebuild the dependencies: '
                         'conda and npm')
parser.add_argument('--database', '-d',
                    action="store_true",
                    help='rebuild the database')
parser.add_argument('--setup', '-s',
                    action="store_true",
                    help='update dependencies and database, '
                         "but don't run the servers")


args = parser.parse_args()

rebuild = args.rebuild
build_database = args.database

run_servers = True
if args.setup:
    rebuild = True
    build_database = True
    run_servers = False

pids = []


if rebuild:
    # make sure conda packages are all up to date
    print("updating / installing all conda packages")
    run(["conda", "install", "-y",
         "--file", "web_api/conda_requirements.txt",
         "--file", "adios_db/conda_requirements.txt",
         "--file", "web_client/conda_requirements.txt",
         ])
    # run(["python", "-m", "pip", "install", "-r",
    #      "web_api/pip_requirements.txt"])

# start up mongo:
mongo = Popen(['mongod', '-f', 'mongo_config_dev.yml'])
pids.append(mongo.pid)

# print("after starting mongo")
if build_database:
    run("oil_db_init")
    run(["oil_db_import", "--all"])

if run_servers:
    webapi = Popen(['pserve', '--reload', 'web_api/config-example.ini'])
    pids.append(webapi.pid)


# ######
#  Client
os.chdir('web_client')

if rebuild:
    # make sure npm packages are up to date
    print("Updating/installing npm packages")
    run(["npm", "install"])
    print("Done with npm packages")

if run_servers:
    print("Starting up Ember Serve")
    client = Popen(['ember', 'serve'])
    pids.append(client.pid)

os.chdir('..')
#  Client
# ######

# still may need this for mongod: used to rebuild database
pids.insert(0, os.getpid())
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

if run_servers:

    wait_for_client_server()
    webbrowser.open('http://localhost:4200/', new=1)

    while True:
        print("App running: http://localhost:4200/")
        print("Hit ^C To stop:")
        time.sleep(2.0)

