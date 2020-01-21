#!/usr/bin/env python

"""
Startup script for web_api for ADIOS OIl Database

This version gets its settings from a JSON file.

Usage:

python run_web_api.py stand_alone_config.json

NOTE: this is missing logger configuration -- that should be added.
"""

# set up the global config
# 'here' is the dir we are running from
#  fixme: maybe this should be derived from the location of the settings file?
#         though I'm not sure how this information is used anyway
import sys
from pathlib import Path
import json
import logging.config

import waitress
import oil_database_api

if __name__ == "__main__":
    try:
        settings_file = sys.argv[1]
    except IndexError:
        print("you need to pass a settings JSON fileon the command line")
        sys.exit(1)


_file = Path(__file__).resolve()
here = _file.parent
settings_path = Path(settings_file).resolve().parent

global_config = {'here': here,
                 '__file__': _file,
                 }

# load settings from JSON file
with open(settings_file) as settings:
    settings = json.load(settings)

# find install info:
install_path = Path(oil_database_api.__file__).parent
help_dir = install_path / "help"

settings['install_path'] = install_path,
settings['help_dir'] = help_dir

# pull the API info from the settings:
api_host = settings.pop("web_api_host")
api_port = settings.pop("web_api_port")

# Set path to serve standalone:
if settings.get('standalone'):
    # Set the path for serving the files
    # assume the client path is realtive to main settings file
    settings['client_path'] = str((settings_path /
                                   settings.pop('client_path')).resolve())
    # Set up CORS policy for stand alone
    # This assures the we're using the right ports, etc.
    # it will override anything in the settings JSON file
    # fixme:should this be automatic for all deployments?
    settings["cors_policy.origins"] = [f"http://0.0.0.0:{api_port}",
                                       f"http://localhost:{api_port}"
                                       ]


# Configure the logger:
# NOTE: we could do this all in the JSON:
#       https://gist.github.com/pmav99/49c01313db33f3453b22
# assume the log config file is next to the main settings file
# log_config_file = settings_path / settings.pop("log_config_file")
# logging.config.fileConfig(log_config_file)


# create the app
app = oil_database_api.main(global_config, **settings)

# start the server
waitress.serve(app, host=api_host, port=api_port)

