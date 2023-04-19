"""
Environment & Climate Change Canada (ECCC) has now published the old oil
catalog book data from 1999 in electronic form.  The .csv flat file for this
is currently found at:

    ('https://data-donnees.ec.gc.ca/data/substances/scientificknowledge/'
     'a-catalogue-of-crude-oil-and-oil-product-properties-1999-revised-2022/'
     'Flat_CSV-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_(1999)-'
     'Revised_2022_En.csv')

One of the priorities with this new data set is to determine if any of these
records are redundant Adios records.  For this, we wrote this script to
iterate through the ECCC records and build an association list of Adios records
that have a similar name.

The idea is to have some corresponding data points from the eccc and Adios
oil records organized in a way to make side-by-side comparison easy,
or at least possible.
"""
import sys
import os
import io
import logging
import traceback
import csv
from argparse import ArgumentParser

from adios_db.util.term import TermColor as tc
from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings, default_settings
from adios_db.models.oil.validation.validate import validate_json
from adios_db.models.oil.completeness import set_completeness

from adios_db.data_sources.env_canada.v3 import (EnvCanadaCsvFile1999,
                                                 EnvCanadaCsvRecordParser1999,
                                                 EnvCanadaCsvRecordMapper1999)

logger = logging.getLogger(__name__)


def print_stack_trace(e, oil_obj):
    print('{} for {}: {}'
          .format(e.__class__.__name__,
                  tc.change(oil_obj.oil_id, 'red'), e))

    depth = 3
    _, exc_value, exc_traceback = sys.exc_info()
    if exc_value is not None:
        tb = traceback.extract_tb(exc_traceback)

        if len(tb) > depth:
            print([_trace_item(*i) for i in tb[-depth:]])
        else:
            print([_trace_item(*i) for i in tb])


def _trace_item(filename, lineno, function, text):
    return {'file': filename,
            'lineno': lineno,
            'function': function,
            'text': text}


argp = ArgumentParser(description='Database Backup Arguments:')
argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))
argp.add_argument('--source', nargs=1,
                  help=('Specify the path to the ECCC source data file.  '
                        'This must be a .csv file.'))
argp.add_argument('--output', nargs=1,
                  help=('Specify the path of a file that we will '
                        'write our results to.'))


def compare_eccc_oils_cmd(argv=sys.argv):
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
        source_file = normalize_file(args.source[0], 'Source file')
        output_file = normalize_file(args.output[0], 'Output file')
    except Exception as e:
        print(e)
        argp.print_help()
        exit(1)

    try:
        compare_eccc_oils(settings, source_file, output_file)
    except Exception:
        print('{0}() FAILED!!!\n'.format(compare_eccc_oils.__name__))
        raise

    exit(0)


def normalize_file(source_file, file_description='File'):
    """
    Basically we want to make sure our file isn't empty.
    Also, if the file extension is missing, default to .csv.
    There may be other criteria in the future but for now, that's it.
    """
    if source_file is None:
        raise ValueError(f'{file_description} not specified!')

    print(f'splitting filename: {source_file}')
    base, name = os.path.split(source_file)

    if len(name) < 1:
        # empty file name
        raise ValueError(f'{file_description}: Empty file name specified '
                         'for source file!')

    if len(name.split(os.path.extsep)) < 2:  # no file extension specified
        name = os.path.extsep.join([name, 'csv'])

    return os.path.join(base, name)


def compare_eccc_oils(settings, source_file, output_file):
    """
    Here is where we read our source data file, which should be the ECCC
    .csv data file.

    For each record we retrieve, we search the database for any records that
    seem like a close match (doesn't need to be exact).

    For each record in our search results, we then write an information set
    containing data from our source record and the corresponding data from our
    matching record. This is for the purpose of comparing the two records.
    """
    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    if settings['mongodb.database'] not in client.list_database_names():
        print(f'The {settings["mongodb.database"]} database does not exist!')
        return

    db = client.get_database(settings['mongodb.database'])
    oil_collection = db.oil

    with EnvCanadaCsvFile1999(source_file) as reader, open(output_file, 'w', newline='') as out_fd:
        writer = csv.writer(out_fd, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        write_header(writer)

        for record_data in reader.get_records():
            try:
                oil_mapper = EnvCanadaCsvRecordMapper1999(
                    EnvCanadaCsvRecordParser1999(*record_data)
                )
                oil_pyjson = oil_mapper.py_json()

                oil = validate_json(oil_pyjson)
                set_completeness(oil)
            except (ValueError, TypeError) as e:
                print_stack_trace(e, oil_mapper)

            print(f'oil_id: {oil.oil_id}, oil_name: {oil.metadata.name}')

            for r in find_matching_oils(oil_collection, oil.metadata.name):
                adios_oil = validate_json(r)

                write_data_row(writer, oil, adios_oil)

    print('\nFinished comparing the ECCC records!\n')


def find_matching_oils(collection, query_string):
    return collection.find({
        'metadata.name': {
            '$regex': query_string, '$options': 'i'
        },
    })


def write_header(writer):
    writer.writerow([
        'ECCC Oil ID',
        'ECCC Oil Name',
        'Adios Oil ID',
        'Adios Oil Name',
        'Adios Reference Year',
        'Adios Reference'
    ])


def write_data_row(writer, eccc_oil, adios_oil):
    writer.writerow([
        eccc_oil.oil_id,
        eccc_oil.metadata.name,
        adios_oil.oil_id,
        adios_oil.metadata.name,
        adios_oil.metadata.reference.year,
        adios_oil.metadata.reference.reference,
    ])
