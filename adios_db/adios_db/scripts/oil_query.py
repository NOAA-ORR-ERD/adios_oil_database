"""
Utility to query the oil database
"""
import sys
import os
import logging
from argparse import ArgumentParser

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings

logger = logging.getLogger(__name__)


argp = ArgumentParser(description='Database Query Arguments:')

argp.add_argument('--query', action='store_true',
                  help=(''))
argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))


def oil_query_cmd(argv=sys.argv):
    """
    command-line parsing our oil_query.

    Examples of how we want to use this on the command-line:

    - oil_query  # fails.  We need to specify something

    - oil_query -k <identifier> (--key=<identifier>)
      This will query for a single oil identified by its ID

    - oil_query -q <query_string> (--query=<query_string>)
      This will search for all records that match the criteria
      specified in the query string.

    The query string will consist of comma separated specifiers:

        "<specifier1>, <specifier2>, ... <specifierN>"

    Each specifier provides increased filtering of results.  A specifier
    has the format:

    "option=filter"
    """

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    if len(argv) < 2:
        oil_query_usage(argv)

    export_file = argv[1]

    if len(argv) >= 3:
        settings = file_settings(argv[2])
    else:
        settings = default_settings()

    try:
        oil_query(settings, export_file)
    except Exception:
        print('{0}() FAILED\n'.format(oil_query.__name__))
        raise


def oil_query_usage(argv):
    cmd = os.path.basename(argv[0])

    print('usage: {0} <export_file> [config_file]\n'
          '(example: "{0} ec_export.csv")'
          .format(cmd))

    sys.exit(1)


def oil_query(settings, export_file):
    logger.info('connect_mongodb()...')
    connect_mongodb(settings)
