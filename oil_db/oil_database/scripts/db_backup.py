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

logger = logging.getLogger(__name__)

argp = ArgumentParser(description='Database Backup Arguments:')

argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))

argp.add_argument('--path', nargs=1,
                  help=('Specify a path to a data storage area (filesystem). '
                        'If not specified, the default is to use "./data"'))


def backup_db_cmd(argv=sys.argv):
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
        backup_db(settings, base_path)
    except Exception:
        print('{0}() FAILED\n'.format(backup_db.__name__))
        raise


def backup_db(settings, base_path):
    '''
        Here is where we backup our database.  This is what we want to do:
        - If the database does not exist, we flag an error and exit:
        - If the database is already there:
            - Gather the collections by name
            - We want to start with an empty folder, so clear the base path
            - For each collection:
                - Create a subfolder under our path using the collection name
                - Iterate the objects in the collection
                - Save the objects as <basepath>/<collection>/<object>
    '''
    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    if settings['mongodb.database'] not in client.list_database_names():
        print(f'The {settings["mongodb.database"]} database does not exist!')
        return

    db = getattr(client, settings['mongodb.database'])
    collections = db.collection_names()

    cleanup_folder(base_path)

    for collection_name in collections:
        add_folder(base_path, collection_name)

        collection = getattr(db, collection_name)

        for rec in collection.find({}):
            export_to_file(base_path, collection_name, rec)
            pass

    print('\nDatabase backup done!\n')


def cleanup_folder(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}: {e}')
    except FileNotFoundError:
        add_folder('.', folder)


def add_folder(base_path, folder):
    folder = os.path.join(base_path, folder)

    if not os.path.exists(folder):
        os.mkdir(folder)


def export_to_file(base_path, collection_name, record):
    record_name = str(record['_id'])

    if collection_name == 'oil':
        # there could be a lot of oil records, so we want to break them up by
        # prefix
        add_folder(os.path.join(base_path, collection_name), record_name[:2])

        filename = os.path.join(base_path, collection_name,
                                record_name[:2], f'{record_name}.json')
    else:
        filename = os.path.join(base_path, collection_name,
                                f'{record_name}.json')

    json.dump(record, open(filename, 'w'),
              default=json_handle_unparseable,
              sort_keys=True, indent=4)


def json_handle_unparseable(o):
    '''
        This is only necessary if we are using the builtin json module
        ujson and orjson have no problems with datetime content.
    '''
    if isinstance(o, ObjectId):
        return str(o)
    elif isinstance(o, datetime.datetime):
        return o.isoformat()
