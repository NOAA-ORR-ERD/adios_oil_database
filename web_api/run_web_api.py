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
_file = Path(__file__).resolve()
here = _file.parent

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

# create the app
app = oil_database_api.main(global_config, **settings)

# start the server
waitress.serve(app, host=api_host, port=api_port)


