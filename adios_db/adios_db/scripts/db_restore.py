import sys
import os
import io
import json
import logging
from argparse import ArgumentParser

from bson import ObjectId

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings
from adios_db.db_init.database import drop_db, create_indices
from adios_db.models.oil.oil import Oil
from bson.errors import InvalidId


logger = logging.getLogger(__name__)

argp = ArgumentParser(description='Database Restore Arguments:')

argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))

argp.add_argument('--path', nargs=1,
                  help=('Specify a path to a data storage area (filesystem). '
                        'If not specified, the default is to use "./data"'))


def restore_db_cmd(argv=sys.argv):
    # make stderr unbuffered
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO)

    args = argp.parse_args(argv[1:])

    if args.config is not None:
        settings = file_settings(args.config)
    else:
        print('Using default settings')
        settings = default_settings()

    base_path = args.path if args.path is not None else './data'

    try:
        restore_db(settings, base_path)
    except Exception:
        print('{0}() FAILED\n'.format(restore_db.__name__))
        raise


def restore_db(settings, base_path):
    '''
    Here is where we restore our database.  This is what we want to do:

    If the restore path does not exist, we flag an error and exit.

    Otherwise:

    - If the database does not exist, create it

    - If the database is already there, initialize it

    - Gather the collection names by directory name

    - For each collection name:

        - create the collection

        - for each object in the collection directory

            - Save the objects
    '''
    if not os.path.exists(base_path):
        print(f'No path named {base_path}!')
        return

    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    drop_db(client, settings['mongodb.database'])

    db = getattr(client, settings['mongodb.database'])

    create_indices(db)

    # load the database
    for collection_name in os.listdir(base_path):
        # filter out dotfiles
        if not collection_name.startswith("."):
            load_collection(db, base_path, collection_name)

    print('\nDatabase restore done!\n')


def load_collection(db, base_path, collection_name):
    collection = getattr(db, collection_name)
    collection_path = os.path.join(base_path, collection_name)

    for (dirname, _, filenames) in os.walk(collection_path):
        for name in filenames:
            if name.endswith('.json'):
                obj = get_obj_json(f'{dirname}/{name}', collection_name)

                collection.insert_one(obj)


def get_obj_json(obj_path, collection_name):
    obj = json.load(open(obj_path, 'r'))

    if collection_name == 'oil':
        oil = Oil.from_py_json(obj)
        oil.reset_validation()
        obj = oil.py_json()

    return obj
