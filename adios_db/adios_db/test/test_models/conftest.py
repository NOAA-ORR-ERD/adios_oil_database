import os

from configparser import ConfigParser

from adios_db.util.db_connection import connect_mongodb


def db_setup():
    # called for running each test in 'a' directory
    config_path = os.path.join(os.path.dirname(__file__),
                               '..', '..', '..',
                               'config-example.ini')

    config = ConfigParser()
    config.read(config_path)

    print(config)

    settings = dict(config['app:adios_db'].items())

    return connect_mongodb(settings)
