import sys
import os
import io
import json
import logging
from argparse import ArgumentParser
from pathlib import Path

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings
from adios_db.db_init.database import drop_db, create_indices
from adios_db.models.oil.oil import Oil


logger = logging.getLogger(__name__)

argp = ArgumentParser(description='Database Restore Arguments:')

argp.add_argument('--config',
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))

argp.add_argument('--path', default='./data',
                  help=('Specify a path to a data storage area (filesystem). '
                        'If not specified, the default is to use "./data"'))


def restore_db_cmd(argv=sys.argv):
    # Python 3 has made stderr buffered, so we have to fix it.
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
        restore_db(settings, args.path)
    except Exception:
        print('{0}() FAILED\n'.format(restore_db.__name__))
        raise


def restore_db(settings, base_path):
    """
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
    """
    base_path = Path(base_path)
    if base_path.exists() and base_path.is_dir():
        logger.info(f'Using path: {base_path}')
    elif base_path.exists():
        print(f'Path {base_path}: not a directory!')
        return
    else:
        print(f'No path named {base_path}!')
        return

    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    drop_db(client, settings['mongodb.database'])

    db = client.get_database(settings['mongodb.database'])

    create_indices(db)

    # load the database
    for collection_name in get_collection_names(settings, base_path):
        load_collection(db, base_path, collection_name)

    for bucket in settings['gridfs.buckets']:
        load_gridfs_bucket(client, base_path, bucket)

    print('\nDatabase restore done!\n')


def get_collection_names(settings, base_path):
    """
    Basically any folder that is in our base path that is not managed as a
    GridFS bucket.  So our criteria are:
        - gotta be a directory
        - can't be a dot file
        - can't be a bucket
    """
    buckets = settings['gridfs.buckets']

    return [f.name for f in base_path.iterdir()
            if f.is_dir()
            and not f.name.startswith(".")
            and not any([f.name.startswith(b) for b in buckets])]


def load_collection(db, base_path, collection_name):
    collection = getattr(db, collection_name)
    collection_path = os.path.join(base_path, collection_name)

    for (dirname, _, filenames) in os.walk(collection_path):
        for name in filenames:
            oil_path = Path(dirname) / name

            if (oil_path.suffix == '.json' and
                    len(validate_oil_id(oil_path.stem)) == 0):
                obj = get_obj_json(oil_path, collection_name)

                collection.insert_one(obj)


def get_obj_json(obj_path, collection_name):
    obj = json.load(open(obj_path, 'r', encoding='utf-8'))

    if collection_name == 'oil':
        oil = Oil.from_py_json(obj)
        oil.reset_validation()
        obj = oil.py_json()

    return obj


def load_gridfs_bucket(client, base_path, bucket):
    """
    The way we are organizing our GridFS buckets is by attaching the bucket
    handler object(s) to the main session object.  This object has an
    attribute name that is the same as the bucket name, and it has a
    consistent API for managing files through GridFS.

    The way we manage the files in the noaa-oil-data repo, is that everything
    hangs off of an oil record.  So the files in our buckets are arranged
    like so:

    Oil record:    f'data/oil/{prefix}/{oil_id}.json'
    Bucket record: f'data/oil/{prefix}/{oil_id}.{bucket}/{filename}'

    Currently, there is only one bucket (attachments), so this translates to:
        f'data/oil/{prefix}/{oil_id}.attachments/{attachment_name}'
    """
    if bucket not in client.__dict__.keys():
        logger.info(f'No bucket found by the name "{bucket}".')
        return
    else:
        logger.info(f'Bucket found: "{bucket}"')

    base_path = base_path / 'oil'
    gfs = getattr(client, bucket)

    total = 0
    for source_path in base_path.rglob('**/*'):
        total += load_gridfs_file(gfs, base_path, source_path)

    logger.info(f'"{bucket}": restoration complete ({total} files loaded).')


def load_gridfs_file(gfs, base_path, source_path):
    """
    Returns the number of files that got loaded.  This instead of a
    boolean return value is because we would like to keep a count of files
    that were loaded.
    """
    if not validate_source_path(source_path, base_path, gfs.bucket_name):
        return 0

    try:
        oil_id, filename = source_path.parts[-2:]
        oil_id, _bucket_name = oil_id.split('.')

        extra_fields = get_extra_fields(source_path)

        with open(source_path, 'rb') as file_obj:
            gfs.insert_one(oil_id, filename, file_obj=file_obj,
                           **extra_fields)
    except Exception as e:
        logger.error(f'"{source_path}": Exception({e})')
        return 0

    return 1


def validate_source_path(source_path, base_path, bucket_name):
    """
    Return True if validated ok, False if failed.

    There are a lot of checks because we are mixing our oil records in with
    our attachment records.
    """
    if source_path.is_dir():
        # logger.warn(f'{source_path}: is a directory.  Skipping...')
        return False

    if base_path.parts != source_path.parts[:len(base_path.parts)]:
        logger.warn(f'{source_path} is not located inside {base_path}.  '
                    'Skipping...')
        return False

    gfs_path = Path(*source_path.parts[len(base_path.parts):])

    if len(gfs_path.parts) != 3:
        # logger.warn(f'{gfs_path}: does not have 3 parts. '
        #             'Path should fit the format '
        #             '"{prefix}/{oil_id}.{bucket_name}/{filename}".  '
        #             'Skipping...')
        return False

    try:
        _prefix, oil_id, filename = gfs_path.parts
        oil_id, bucket_name_in_path = oil_id.split('.')
    except ValueError as e:
        logger.warn(f'{gfs_path} cannot be parsed as expected.  '
                    f'Exception: {e}\n'
                    'Skipping...')
        return False

    warnings = validate_oil_id(oil_id)
    if len(warnings) > 0:
        logger.warn(f'File: {filename}, Oil ID: {oil_id}, '
                    f'Warnings: {warnings}\n'
                    'Skipping...')
        return False

    if bucket_name_in_path != bucket_name:
        logger.warn(f'{bucket_name_in_path} is the wrong bucket name '
                    f'(should be {bucket_name}).  Skipping...')
        return False

    if filename.endswith('.field.json'):
        # logger.warn(f'{filename} is designated to contain GridFS '
        #             'extra field data.  Skipping...')
        return False

    logger.info(f'{gfs_path} parsed OK.')

    return True


def validate_oil_id(oil_id):
    """
    We would like our attachments (as well as any other potential bucket items)
    to be associated with oils in our database.  But we want the coupling to be
    pretty loose.  So we don't require an existing oil, but we do at least
    warn if a particular file doesn't reference an oil ID that looks valid.

    This doesn't stop the operation, but does raise warnings.

    TODO: I feel this might be redundant code that could be put in a
    common area.
    """
    warnings = []

    if not oil_id[:2].isalpha():
        warnings.append(f'Oil ID prefix: {oil_id[:2]} not alphabetical')

    if not oil_id[:2].isupper():
        warnings.append(f'Oil ID prefix: {oil_id[:2]} not uppercase')

    if not oil_id[2:].isdigit():
        warnings.append(f'Oil ID : {oil_id[2:]} not numeric')

    return warnings


def get_extra_fields(source_path):
    field_path = source_path.parent / f'{source_path.stem}.field.json'

    if field_path.exists():
        return json.load(open(field_path, 'r', encoding='utf-8'))
    else:
        return {}
