#!/usr/bin/env python

"""
Script to build the stand alone

Written in Python so it will run cross platform.
 - If this gets to be a pain, we can make a Windows batch
   file and/or *nix shell script

So far, only sets it up in a dir that maybe can be
built into an installer some day?
"""
import sys
from os import chdir
from shutil import copytree, rmtree
from subprocess import run

# fixme: smarter argument parsing might be good
nodeps = True if "--nodeps" in sys.argv else False


# ################
# Set up the client:

# first get all depedencies, etc. intstalled
chdir('web_client')


# make sure npm packages are up to date
if not nodeps:
    print("Updating/installing npm packages")
    run(["npm", "install"])
    print("Done with npm packages")

# build the ember app
run(["ember", "build", "--prod", "-o", "client_code"])

# copy the ember app to the StandAlone dir
# remove any old code:
rmtree("../StandAlone/client_code", ignore_errors=True)
copytree("client_code", "../StandAlone/client_code", )

chdir("..")
# ################





