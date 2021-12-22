import sys
import os
import io
import logging
from argparse import ArgumentParser

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings
from adios_db.db_init.labels import load_labels, print_all_labels
from adios_db.db_init.database import drop_db, create_indices

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
    # Python 3 has made stderr buffered, so we have to fix it
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


def init_db(settings, show_prompt=True):
    """
    Here is where we create and initialize our database.  This is what
    we want to do:

    - if the database is already there, we prompt for recreation

    - if the database does not exist, or we are prompted for recreation:

        - drop the database

        - create the tables (if necessary)

        - load the basic infrastructure data:

            - Labels
    """
    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    if show_prompt:
        if settings['mongodb.database'] in client.list_database_names():
            if prompt_drop_db():
                print('Alright then...continuing on...')
            else:
                print('Ok, quitting the database initialization now...')
                return

    drop_db(client, settings['mongodb.database'])

    db = client.get_database(settings['mongodb.database'])

    print()
    load_labels(db)

    print_all_labels(db)

    create_indices(db)

    print('\nDatabase initialization done!\n')


def prompt_drop_db():
    resp = input('This action will permanently delete all data in the '
                 'existing database!\n'
                 'Are you sure you want to re-initialize it? (y/n): ')
    return len(resp) > 0 and resp.lower()[0] == 'y'
