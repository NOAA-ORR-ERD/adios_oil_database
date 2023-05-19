import sys

from adios_db.util.db_connection import connect_mongodb

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)


client = connect_mongodb({'mongodb.host': 'localhost',
                          'mongodb.port': 27017,
                          'mongodb.database': 'adios_db',
                          'mongodb.alias': 'oil-db-app'})
db = client.adios_db
records = db.imported_record
oils = db.oil


def deep_get(obj, attr_path, default=None):
    if isinstance(attr_path, str):
        attr_path = attr_path.split('.')

    attrs, current = attr_path, obj

    try:
        for p in attrs:
            current = current[p]

        return current
    except KeyError:
        return default


def to_field(value):
    '''
        Some fields, like the reference, contain newlines.  This messes up
        our attempt at parsing a single row per record because a newline is
        our row delimiter.
    '''
    try:
        return ' '.join(value.split('\n'))
    except Exception:
        return value


for attr in ('ID', 'Name', 'Reference', 'Sample Date', 'Location',
             'Product Type', 'Labels', 'API'):
    sys.stdout.write(f'{attr}\t')

sys.stdout.write('\n')


for o in oils.find():
    sys.stdout.write(f'{o["_id"]}\t')

    for attr in ('name', 'reference.reference', 'sample_date', 'location',
                 'product_type', 'labels', 'API'):
        v = deep_get(o['metadata'], attr)
        if v is None:
            sys.stdout.write('\t')
        else:
            v = to_field(v)
            sys.stdout.write(f'{v}\t')

    sys.stdout.write('\n');
