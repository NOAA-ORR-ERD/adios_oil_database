import sys
import os
import logging
from pprint import PrettyPrinter

from pymongo.errors import ConnectionFailure

from oil_database.util.db_connection import connect_modm
from oil_database.util.settings import file_settings, default_settings

from oil_database.db_init.categories import (load_categories,
                                             print_all_categories)


logger = logging.getLogger(__name__)

pp = PrettyPrinter(indent=2, width=120)

# All oil library data files are assumed to be in a common data folder
data_path = os.path.sep.join(__file__.split(os.path.sep)[:-3] + ['data'])


def init_db_cmd(argv=sys.argv):
    logging.basicConfig(level=logging.INFO)

    if len(argv) >= 2:
        # we will assume that if a file is specified, it will contain all
        # necessary settings.
        settings = file_settings(argv[1])
    else:
        settings = default_settings()

    try:
        init_db(settings)
    except Exception:
        print "{0}() FAILED\n".format(init_db.__name__)
        raise


def init_db_usage(argv):
    cmd = os.path.basename(argv[0])

    print('usage: {0} [config_file]\n'
          '(example: "{0}")'.format(cmd))

    sys.exit(1)


def init_db(settings):
    '''
        Here is where we create and initialize our database.  This is what
        we want to do:
        - if the database is already there, we prompt for recreation
        - if the database does not exist, or we are prompted for recreation:
            - drop the database
            - create the tables (if necessary)
            - load the basic infrastructure data:
                - Categories

    '''
    logger.info('connect_modm()...')
    client = connect_modm(settings)

    if settings['mongodb.database'] in client.database_names():
        if prompt_drop_db():
            print 'Alright then...continuing on...'
        else:
            print 'Ok, quitting the database initialization now...'
            return

    drop_db(client, settings['mongodb.database'])

    load_categories()

    print ('printing all categories...')
    print_all_categories()


def prompt_drop_db():
    resp = raw_input('This action will permanently delete all data in the '
                     'existing database!\n'
                     'Are you sure you want to re-initialize it? (y/n): ')
    return len(resp) > 0 and resp.lower()[0] == 'y'


def drop_db(client, db_name):
    print 'dropping db {}...'.format(db_name)
    try:
        if db_name in client.database_names():
            print 'Dropping database "{}"...'.format(db_name),
            client.drop_database(db_name)
            print 'Dropped'
    except ConnectionFailure:
        print 'Could not connect to MongoDB!'
        raise
    except Exception:
        print 'Failed to drop Oil database!'
        raise
