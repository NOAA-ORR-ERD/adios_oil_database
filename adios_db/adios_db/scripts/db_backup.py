import sys
import os
import io
import shutil
import datetime
import logging
import json
from argparse import ArgumentParser
from pathlib import Path

from bson import ObjectId

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings
from adios_db.models.oil.oil import Oil


logger = logging.getLogger(__name__)

argp = ArgumentParser(description='Database Backup Arguments:')

argp.add_argument('--config',
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))

argp.add_argument('--path', default='./data',
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

    try:
        backup_db(settings, args.path)
    except Exception:
        print('{0}() FAILED\n'.format(backup_db.__name__))
        raise


def backup_db(settings, base_path):
    """
    Here is where we backup our database.  This is what we want to do:

    - If the database does not exist, we flag an error and exit:
    - If the database is already there:
        - Gather the collections by name
        - We want to start with an empty folder, so clear the base path
        - For each collection:
            - Create a subfolder under our path using the collection name
            - Iterate the objects in the collection
            - Save the objects as <basepath>/<collection>/<object>
    """
    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    if settings['mongodb.database'] not in client.list_database_names():
        print(f'The {settings["mongodb.database"]} database does not exist!')
        return

    db = client.get_database(settings['mongodb.database'])

    collections = get_collection_names(settings, db)
    logger.info(f'Found the following collections: {collections}')

    logger.info(f'cleanup_folder({base_path})...')
    cleanup_folder(base_path)

    for collection_name in collections:
        add_folder(base_path, collection_name)

        collection = getattr(db, collection_name)

        for rec in collection.find({}):
            export_to_file(rec, base_path, collection_name)

    for bucket in settings['gridfs.buckets']:
        export_gridfs_bucket(client, base_path, bucket)

    print('\nDatabase backup done!\n')


def get_collection_names(settings, db):
    """
    Get all collections except the ones associated to GridFS buckets.
    They are managed in a different way.
    """
    return [c for c in db.list_collection_names()
            if not any([c.startswith(b) for b in settings['gridfs.buckets']])]


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


def export_to_file(record, base_path, collection_name='oil'):
    """
    export a record to a json file

    :param record: py_json of a full record
    :param base_path: path to the dir in which to dump the data
    :param collection_name='oil': which collection to dump -- 'oil' by default'
    """
    base_path = Path(base_path)

    if collection_name == 'oil':
        record = Oil.from_py_json(record)

        # remove the status
        record.status = []
        # remove the gnome_suitable flag
        record.metadata.gnome_suitable = None
        record_name = record.oil_id

        # There are a lot of oil records, so we want to break them up by
        # prefix
        data_path = base_path / "oil" / record_name[:2]
        data_path.mkdir(parents=True, exist_ok=True)

        filename = data_path / f'{record_name}.json'
        record.to_file(filename)
    else:
        record_name = str(record['_id'])
        filename = os.path.join(base_path, collection_name,
                                f'{record_name}.json')

        with open(filename, 'w', encoding="utf-8") as outfile:
            json.dump(record, outfile, indent=4,
                      default=json_handle_unparseable)


def json_handle_unparseable(o):
    """
    This is only necessary if we are using the builtin json module
    ujson and orjson have no problems with datetime content.
    """
    if isinstance(o, ObjectId):
        return str(o)
    elif isinstance(o, datetime.datetime):
        return o.isoformat()


def export_gridfs_bucket(client, base_path, bucket):
    """
    The way we are organizing our GridFS buckets is by attaching the bucket
    handler object(s) to the main session object.  This object has an
    attribute name that is the same as the bucket name, and it has a
    consistent API for managing files through GridFS.
    """
    if bucket not in client.__dict__.keys():
        logger.info(f'No bucket found by the name "{bucket}".')
        return
    else:
        logger.info(f'Bucket found: "{bucket}"')

    gfs = getattr(client, bucket)

    total = 0
    for file_path in gfs.list():
        total += export_gridfs_file(gfs, base_path, Path(file_path))

    logger.info(f'"{bucket}": file backup complete ({total} files saved).')


def export_gridfs_file(gfs, base_path, file_path):
    try:
        _prefix, oil_id, filename = file_path.parts

        # out_path = Path(base_path, gfs.bucket_name, file_path)
        out_path = Path(base_path, 'oil', _prefix,
                        f'{oil_id}.{gfs.bucket_name}', filename)

        warnings = validate_oil_id(oil_id)
        if len(warnings) > 0:
            logger.warn(f'File: {file_path}, Oil ID: {warnings}')

        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, 'wb') as file_obj:
            file_obj.write(gfs.find_one(oil_id, filename).read())

        fields_out_path = out_path.parent / f'{out_path.stem}.field.json'

        with open(fields_out_path, 'w') as file_obj:
            file_obj.write(json.dumps(
                gfs.get_extra_fields(oil_id, filename)
            ))
    except Exception as e:
        logger.error(f'"{file_path}": Exception({e})')
        return 0

    return 1


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
