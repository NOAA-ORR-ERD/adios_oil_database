'''
    This is where we handle the creation and initialization of the oil
    database.
'''
import logging

from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)


def drop_db(client, db_name):
    print('\nDropping db {}...'.format(db_name))
    try:
        if db_name in client.list_database_names():
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
        # db.oil.create_index([('name', ASCENDING),
        #                      ('location', ASCENDING),
        #                      ('reference_date', ASCENDING)],
        #                     unique=True)
        print('Oil collection indices: {}'
              .format(list(db.oil.index_information().keys())))
    except ConnectionFailure:
        print('Could not connect to MongoDB!')
        raise
    except Exception:
        print('Failed to drop Oil database!')
        raise
