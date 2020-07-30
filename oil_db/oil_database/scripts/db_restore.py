import sys
import os
import shutil
import io
import json
import datetime
import logging
from argparse import ArgumentParser

from bson import ObjectId

from oil_database.util.db_connection import connect_mongodb
from oil_database.util.settings import file_settings, default_settings
from oil_database.db_init.database import drop_db, create_indices

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
        - If the restore path does not exist, we flag an error and exit:
        - Otherwise:
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

    # load the database
    for collection_name in os.listdir(base_path):
        load_collection(db, base_path, collection_name)

    create_indices(db)

    print('\nDatabase restore done!\n')


def load_collection(db, base_path, collection_name):
    collection = getattr(db, collection_name)
    collection_path = os.path.join(base_path, collection_name)

    for (dirname, _, filenames) in os.walk(collection_path):
        for name in filenames:
            if name.endswith('.json'):
                obj_path = f'{dirname}/{name}'
                obj = json.load(open(obj_path, 'r'))

                fix_obj_id(obj, collection)

                collection.insert_one(obj)


def fix_obj_id(obj, collection):
    '''
        MongoDB uses an ObjectId type for its identifiers in most non special
        cases.  This is not parseable to JSON.  So when backing up our data,
        we turn it into a string.
        This means we need to turn them back into ObjectId's when restoring.
        The collection doesn't seem to have a way of querying the datatype for
        _id, so we need to do this in a more hacked way.
        Right now the only collection that doesn't use the ObjectId type is the
        oil collection, so that's what we will key on.
    '''
    if collection.name != 'oil':
        obj['_id'] = ObjectId(obj['_id'])

    return obj