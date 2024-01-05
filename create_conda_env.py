#!/usr/bin/env python

"""
Very simple script to set up the full environment

Written in Python so it can be the same on all platforms

and an experiment with using the conda API

WARNING: this need to be run from the base environment:
         if run from an activated environment, it will
         create this one inside the other one.
"""

PYTHON_VER = 3.10

import sys
from pathlib import Path
from conda.cli.python_api import run_command, Commands

here = Path(__file__).parent


# create the environment
run_command(Commands.CREATE, ["-n", "adios_db",
                              f"python={PYTHON_VER}"
                              "--file", str(here / "adios_db" / "conda_requirements.txt"),
                              "--file", str(here / "web_api" / "conda_requirements.txt"),
                              ],
                              stdout=sys.stdout,
                              )

