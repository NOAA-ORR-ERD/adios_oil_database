#!/usr/bin/env python

"""
Script to build the stand alone

This should be run from a development environment:
  - Not the standalone environment

Written in Python so it will run cross platform.
 - If this gets to be a pain, we can make a Windows batch
   file and/or *nix shell script

So far, only sets it up in a dir that maybe can be
built into an installer some other way.
"""

import sys
from os import chdir
from shutil import copytree, rmtree
from subprocess import run, Popen
from pathlib import Path


import argparse

# Parse the input arguments
parser = argparse.ArgumentParser()
parser.add_argument("--nodeps", '-n',
                    action="store_true",
                    help="Don't Rebuild the dependencies: "
                         'conda and npm')
parser.add_argument('--nodatabase', '-d',
                    action="store_true",
                    help="don't rebuild the mongo database")
parser.add_argument('--noconda', '-c',
                    action="store_true",
                    help="don't build the standalone conda environment")


args = parser.parse_args()

nodeps = args.nodeps
noconda = args.noconda
nodatabase = args.nodatabase

# utility functions
def get_env_path(env_name):
    env_list = run(['conda', 'env', 'list'], capture_output=True)
    env_list = env_list.stdout.decode().split("\n")
    for line in env_list:
        if line.startswith('#'):
            continue
        name, path = line.split(maxsplit=1)
        if name.strip() == env_name:
            return Path(path.strip())


# Update all the dependencies

# first conda

# first get all dependencies, etc. installed
# fixme -- we could put in a check for the the environment name,
#          so that it wouldn't install into the standalone env

if not nodeps:
    chdir('../')
    # make sure conda packages are all up to date
    print("updating / installing all conda packages")
    run(["conda", "install", "-y",
         "--file", "web_api/conda_requirements.txt",
         "--file", "oil_db/conda_requirements.txt",
         "--file", "web_client/conda_requirements.txt",
         ])
    run(["python", "-m", "pip", "install", "-r",
         "web_api/pip_requirements.txt"])

    # our applications have to be installed, too
    chdir("oil_db")
    run(["pip", "install", "-e", "."])

    chdir("../web_api")
    run(["pip", "install", "-e", "."])
    chdir("..")


    # make sure npm packages are up to date
    chdir('web_client')
    print("Updating/installing npm packages")
    run(["npm", "install"])
    print("Done with npm packages")
    chdir('../StandAlone')


# build the ember app

chdir('../web_client')
run(["ember", "build", "--prod", "-o", "client_code"])

# copy the ember app to the StandAlone dir
# remove any old code:
rmtree("../StandAlone/client_code", ignore_errors=True)
copytree("client_code", "../StandAlone/client_code", )

chdir("../StandAlone")


if not nodatabase:

    # mongod needs to be running to do this
    # start up mongo:
    p = Path("mongo_files")
    if p.exists():
        rmtree(p, ignore_errors=True)
    p.mkdir()
    mongo = Popen(['mongod',
                   '--port', '27017',  # using the standard mongo port,
                                       # as that's hardcoded elsewhere :-(
                   '--dbpath', 'mongo_files',
                   ])

    run(["oil_db_init"])

    run(["oil_db_import --all"], shell=True)

    # and kill it
    mongo.terminate()


if not noconda:
    # build the conda standalone environment
    # NOTE: you still need to install the app pacakges:
    #       oil_database, oil_database_api
    run(['conda',
         'create',
         '-y',
         '-n',
         'standalone',
         '--file',
         'standalone_conda_requirements.txt'])
    # our pacakges need to be installed before copying over.
    # the environment needs to be activated to do that
    # it is NOT easy to script activating the environment
    """
    conda activate standalone
    cd oil_db
    pip install .
    cd ../web_api
    pip install .
    cd ..
    """
    # then you can copy it here:
#    env_path = get_env_path(standalone)
#    rmtree('standalone', ignore_errors=True)
#    copytree(env_path, "./")







