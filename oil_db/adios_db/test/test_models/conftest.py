import os

from configparser import ConfigParser

from oil_database.util.db_connection import connect_mongodb


def db_setup():
    # called for running each test in 'a' directory
    config_path = os.path.join(os.path.dirname(__file__),
                               '..', '..', '..',
                               'config-example.ini')

    config = ConfigParser()
    config.read(config_path)

    print(config)

    settings = dict(config['app:oil_database'].items())

    return connect_mongodb(settings)
