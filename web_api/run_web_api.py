#!/usr/bin/env python

"""
Startup script for web_api for ADIOS OIl Database

From Mike Orr:

Pserve is a wrapper that parses the INI file, instantiates a WSGI
application based on the "[app:main]" section, and a WSGI server based
on the "[server:main]" section, and launches the server with the
application. It also initialized Python logging from the INI file and
has an optional monitor that will restart the application if a file in
it changes (the "--reload" option). The "use = egg:waitress:main"
option is the one that tells it to load Waitress, and the other
options are its arguments.

You can do most this without Pserve something like this:
"""

# import pyramid.paster
# import waitress

# pyramid.paster.setup_logging("config:config-example.ini")
# app = pyramid.paster.get_app("config:config-example.ini")

# waitress.serve(app, host='0.0.0.0', port=8080)



# Or if you have the deployment settings in a dict:

# Fixme: need to set up loggin here
# import logging.config
import waitress
import oil_database_api
import configparser
from pathlib import Path


# logging.config.fileConfig("myloggingconfig.ini")
config = configparser.ConfigParser()
config.read('config-example.ini')
config['app:oil_database_api']

# print(dict(config['app:oil_database_api']))

# set up the global config
# 'here' is the dir we are running from
_file = Path(__file__).resolve()
here = _file.parent

global_config = {'here': here,
                 '__file__': _file,
                 }

# find install info:
install_path = Path(oil_database_api.__file__).parent
help_dir = install_path / "help"


settings = {
            'mongodb.host': "localhost",
            'mongodb.port': "27017",
            'mongodb.database': 'oil_database',
            'mongodb.alias': 'oil-db-app',

            'pyramid.reload_templates': 'true',
            'pyramid.debug_authorization': 'false',
            'pyramid.debug_notfound': 'false',
            'pyramid.debug_routematch': 'false',
            'pyramid.default_locale_name': 'en',
            'pyramid.includes': 'pyramid_tm\ncornice\npyramid_mongodb2',

            'cors_policy.origins': 'http://0.0.0.0:8080\nhttp://localhost:8080\nhttp://localhost:8088\nhttp://localhost:4200\nhttp://localhost:4201',

            'caps.can_modify_db': 'false',

            'install_path': install_path,
            'help_dir': help_dir
            }



app = oil_database_api.main(global_config, **settings)


waitress.serve(app, host='0.0.0.0', port=8080)


