import os

from configparser import ConfigParser


def pytest_runtest_setup(item):
    # called for running each test in 'a' directory
    config_path = os.path.join(os.path.dirname(__file__),
                               '..', '..', '..',
                               'config-example.ini')

    config = ConfigParser()
    config.read(config_path)

    settings = dict(config['app:oil_database'].items())
