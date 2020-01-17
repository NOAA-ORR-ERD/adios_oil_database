import sys
import os
import io
import logging
from argparse import ArgumentParser

from pymongo import ASCENDING
from pymongo.errors import ConnectionFailure

from oil_database.util.db_connection import connect_mongodb
from oil_database.util.settings import file_settings, default_settings

from oil_database.db_init.categories import (load_categories,
                                             print_all_categories)

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)

# All oil library data files are assumed to be in a common data folder
data_path = os.path.sep.join(__file__.split(os.path.sep)[:-3] + ['data'])


argp = ArgumentParser(description='Database Initialization Arguments:')
argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))


def init_db_cmd(argv=sys.argv):
    # Let's give a round of applause to Python 3 for making stderr buffered.
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO)

    args = argp.parse_args(argv[1:])

    if args.config is not None:
        settings = file_settings(args.config)
    else:
        print('Using default settings')
        settings = default_settings()

    try:
        init_db(settings)
    except Exception:
        print('{0}() FAILED\n'.format(init_db.__name__))
        raise


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
    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    if settings['mongodb.database'] in client.list_database_names():
        if prompt_drop_db():
            print('Alright then...continuing on...')
        else:
            print('Ok, quitting the database initialization now...')
            return

    drop_db(client, settings['mongodb.database'])

    db = getattr(client, settings['mongodb.database'])

    print()
    load_categories(db)

    print_all_categories(db)

    create_indices(db)

    print('\nDatabase initialization done!\n')


def prompt_drop_db():
    resp = input('This action will permanently delete all data in the '
                 'existing database!\n'
                 'Are you sure you want to re-initialize it? (y/n): ')
    return len(resp) > 0 and resp.lower()[0] == 'y'


def drop_db(client, db_name):
    print('\nDropping db {}...'.format(db_name))
    try:
        if db_name in client.database_names():
            print('Dropping database "{}"...'.format(db_name), end="")
            client.drop_database(db_name)
            print('Dropped')
    except ConnectionFailure:
        print('Could not connect to MongoDB!')
        raise
    except Exception:
        print('Failed to drop Oil database!')
        raise


def create_indices(db):
    print('\ncreating indices on db {}...'.format(db.name))

    try:
        # We have come to a consensus that unique (name, location, ref)
        # is not necessary.
        #
        #db.oil.create_index([('name', ASCENDING),
        #                     ('location', ASCENDING),
        #                     ('reference_date', ASCENDING)],
        #                    unique=True)
        print('Oil collection indices: {}'
              .format(list(db.oil.index_information().keys())))
    except ConnectionFailure:
        print('Could not connect to MongoDB!')
        raise
    except Exception:
        print('Failed to drop Oil database!')
        raise
