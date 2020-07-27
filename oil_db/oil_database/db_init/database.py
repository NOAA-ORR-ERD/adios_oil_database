'''
    This is where we handle the initialization of the oil labels.

    Basically, we have a number of oil labels which will make it possible
    for users to find oils by the general 'type' of oil they are looking for.

    So we would like each oil to be linked to one or more of these
    labels.  For most of the oils we should be able to do this using
    generalized methods.  But there will very likely be some records
    we just have to link in a hard-coded way.

    The selection criteria for assigning refined products to different
    labels depends upon the API (density) and the viscosity at a given
    temperature, usually at 38 C(100F).  The criteria follows closely,
    but not identically, to the ASTM standards
'''
import logging

from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)


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
