import os

from configparser import SafeConfigParser

from oil_database.util.db_connection import connect_modm


def pytest_runtest_setup(item):
    # called for running each test in 'a' directory
    config_path = os.path.join(os.path.dirname(__file__),
                               '..', '..', '..',
                               'config-example.ini')

    config = SafeConfigParser()
    config.read(config_path)

    settings = dict(config['app:oil_database'].iteritems())

    connect_modm(settings)
