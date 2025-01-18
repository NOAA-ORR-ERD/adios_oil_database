import sys
import os
import io
import logging
import traceback
import pathlib

from datetime import datetime
from argparse import ArgumentParser

from pymongo.errors import DuplicateKeyError

from adios_db.util.term import TermColor as tc
from adios_db.util.db_connection import connect_mongodb
from adios_db.util.folder_collection import FolderCollection
from adios_db.util.settings import file_settings, default_settings

from adios_db.data_sources.noaa_fm import (OilLibraryCsvFile,
                                           OilLibraryRecordParser,
                                           OilLibraryAttributeMapper)

from adios_db.data_sources.env_canada.v2 import EnvCanadaCsvRecordMapper
from adios_db.data_sources.env_canada.v2 import (EnvCanadaCsvFile,
                                                 EnvCanadaCsvRecordParser)

from adios_db.data_sources.env_canada.v3 import (EnvCanadaCsvFile1999,
                                                 EnvCanadaCsvRecordParser1999,
                                                 EnvCanadaCsvRecordMapper1999)

from adios_db.data_sources.exxon_assays import (ExxonDataReader,
                                                ExxonRecordParser,
                                                ExxonMapper)

from adios_db.models.oil.validation.validate import validate_json
from adios_db.models.oil.completeness import set_completeness


logger = logging.getLogger(__name__)

# All oil library data files are assumed to be in a common data folder
data_path = os.path.sep.join(__file__.split(os.path.sep)[:-3] + ['data'])


def _trace_item(filename, lineno, function, text):
    return {'file': filename,
            'lineno': lineno,
            'function': function,
            'text': text}


def not_implemented(_settings):
    print('\tImport of this dataset is not implemented!!')


def add_all(settings):
    """
    Import all valid, available datasets from our menu
    a dataset is valid if it has the full complement of handler classes.
    """
    for item in menu_items:
        if len(item) == 6:
            (label, config,
             record_cls, reader_cls, parser_cls, mapper_cls) = item
            print('\tPerforming import on dataset: {}'.format(label))

            import_records(settings[config],
                           record_cls, reader_cls, parser_cls, mapper_cls,
                           overwrite=settings['overwrite'])


menu_items = (['NOAA Filemaker', 'oildb.fm_files',
               None,
               OilLibraryCsvFile,
               OilLibraryRecordParser,
               OilLibraryAttributeMapper],
              ['Norway Filemaker', 'oildb.nor_files',
               None,
               OilLibraryCsvFile,
               OilLibraryRecordParser,
               OilLibraryAttributeMapper],
              ['Environment Canada', 'oildb.ec_files',
               None,
               EnvCanadaCsvFile,
               EnvCanadaCsvRecordParser,
               EnvCanadaCsvRecordMapper],
              ['Environment & Climate Change Canada (1999)',
               'oildb.eccc_files',
               None,
               EnvCanadaCsvFile1999,
               EnvCanadaCsvRecordParser1999,
               EnvCanadaCsvRecordMapper1999],
              ['Exxon Assays', 'oildb.exxon_files',
               None,
               ExxonDataReader,
               ExxonRecordParser,
               ExxonMapper],
              ['All datasets', add_all]
              )


argp = ArgumentParser(description='Database Import Arguments:')
argp.add_argument('--all', action='store_true',
                  help=('Import all datasets, bypassing the menus, and quit '
                        'the application when finished.'))
argp.add_argument('--overwrite', action='store_true',
                  help=('Overwrite any duplicate records'))
argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))
argp.add_argument('--path', nargs=1,
                  help=('Specify a path to the test data (filesystem). '
                        'If not specified, the default is "./data". '
                        'This option overrides --config.'))


def import_db_cmd(argv=sys.argv):
    # Python 3 has made stderr buffered, so we have to fix it
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO)

    settings = get_settings(argv)

    if 'path' in settings:
        logger.info(f'Using file path: {settings["path"]}')
        data_source = settings['path']
    else:
        logger.info('connect_mongodb()...')
        data_source = connect_mongodb(settings)

    init_menu_item_collections(data_source, settings)

    try:
        if settings['all'] is True:
            add_all(settings)
        else:
            import_db(settings)
    except Exception:
        print("{0}() FAILED\n".format(add_all.__name__))
        raise

    exit(0)


def get_settings(argv):
    args = argp.parse_args(argv[1:])

    if args.path is not None:
        settings = {'path': args.path[0]}
    elif args.config is not None:
        settings = file_settings(args.config)
    else:
        print('Using default settings')
        settings = default_settings()

    _add_datafiles(settings)

    settings['overwrite'] = args.overwrite
    settings['all'] = args.all

    return settings


def import_db(settings):
    """
    Here is where we perform an import of records into our database from
    one or more predefined datasets.

    This is what we want to do:

    - pull up a console menu so the user can choose the dataset to import
    - prompt for a numbered item in the menu or quit response
    - if numbered item:
        - import the chosen item
    - else if quit:
        - exit the program
    - repeat from the beginning
    """
    quit_app = False

    while quit_app is False:
        print_menu()

        choice = prompt_for_menu_item()

        if choice == 'q':
            quit_app = True
        else:
            chosen = get_chosen_menu_item(choice)

            if chosen is None:
                print('\tInvalid Choice...')
            elif len(chosen) == 2:
                label, func = chosen
                print('\tYour choice: {}'.format(label))

                func(settings)
            else:
                (label, config, oil_collection,
                 reader_cls, parser_cls, mapper_cls) = chosen
                print('\tYour choice: {}'.format(label))

                begin = datetime.now()
                import_records(settings[config], oil_collection,
                               reader_cls, parser_cls, mapper_cls,
                               overwrite=settings['overwrite'])
                end = datetime.now()

                print('time elapsed: {}'.format(end - begin))

    print('quitting the import...')


def init_menu_item_collections(client, settings):
    """
    We will be loading everything into the same collection, so we set
    all items to the same place.
    """
    if 'path' in settings:
        # our collection will be a filesystem folder
        oil_collection = FolderCollection(settings['path'])
    else:
        oil_collection = getattr(client, settings['mongodb.database']).oil

    [i.__setitem__(2, oil_collection)
     for i in menu_items
     if len(i) >= 3]


def print_menu():
    print('\nImportable datasets:')

    for idx, item in enumerate(menu_items):
        item_lbl = item[0]
        print('\t{} - {}'.format(idx + 1, item_lbl))


def prompt_for_menu_item():
    resp = (input('Choose a dataset to import or quit (q): ')
            .lower().strip())

    if resp == '':
        resp = 'q'

    return resp


def get_chosen_menu_item(choice):
    try:
        return menu_items[int(choice) - 1]
    except Exception:
        return None


def import_records(config, oil_collection, reader_cls, parser_cls, mapper_cls,
                   overwrite=False):
    """
    Add the records from a data source.
    the config value should be a file list.

    This is meant to be a generic way of reading the source, parsing the
    records, and then mapping them to our Oil object.

    :param config: A string representing a list of files separated by
                   newline characters.  These are understood as a list
                   of files containing the data to import.
    :type config: string or unicode

    :param oil_collection: A database oil collection (table)

    :param reader_cls: A file reader class capable of iterating the records
                       in a data file of a specified type.

    :param parser_cls: A class that is capable of parsing the data in a
                       data record of a specified type.

    :param mapper_cls: A class that can map the data in a particular
                       parser class or storage class into Oil record
                       attributes.
    """
    for fn in config.split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = reader_cls(fn)

        total_count = 0
        success_count = 0
        error_count = 0
        for record_data in fd.get_records():
            total_count += 1

            try:
                oil_mapper = mapper_cls(parser_cls(*record_data))
                oil_pyjson = oil_mapper.py_json()

                oil = validate_json(oil_pyjson)
                set_completeness(oil)

                insert_oil(oil_collection, oil.py_json(), oil_mapper)
            except DuplicateKeyError as e:
                if overwrite is True:
                    try:
                        oil_collection.replace_one({'_id': oil_mapper.oil_id},
                                                   oil.py_json())
                    except Exception as e:
                        print('Oil update failed for {}: {}'
                              .format(tc.change(oil_mapper.oil_id, 'red'), e))
                        error_count += 1
                    else:
                        success_count += 1
                else:
                    print('Duplicate fields for {}: {}'
                          .format(tc.change(oil_mapper.oil_id, 'red'), e))
                    error_count += 1
            except (ValueError, TypeError) as e:
                print('{} for {}: {}'
                      .format(e.__class__.__name__,
                              tc.change(oil_mapper.oil_id, 'red'), e))

                depth = 3
                _, exc_value, exc_traceback = sys.exc_info()
                if exc_value is not None:
                    tb = traceback.extract_tb(exc_traceback)

                    if len(tb) > depth:
                        print([_trace_item(*i) for i in tb[-depth:]])
                    else:
                        print([_trace_item(*i) for i in tb])

                error_count += 1
            else:
                success_count += 1

            if total_count % 100 == 0:
                sys.stderr.write('.')

        print('finished!!!  '
              '{} records processed, '
              '{} records succeeded, '
              '{} records failed,'
              .format(tc.change(total_count, 'bold'),
                      tc.change(success_count, 'bold'),
                      tc.change(error_count, 'bold')))


def insert_oil(collection, py_json, oil_mapper=None):
    py_json.pop('status', None)
    py_json['metadata'].pop('gnome_suitable', None)
    collection.find_one_and_replace({'oil_id': py_json['oil_id']}, py_json,
                                    upsert=True,)

    if hasattr(oil_mapper, 'distillation_cut_set_resolved'):
        # write out the record to local dir
        oil = validate_json(py_json)
        set_completeness(oil)
        oil.metadata.gnome_suitable = None
        oil.status = []

        folder = pathlib.Path('./distillation_cut_set_resolved')
        folder.mkdir(exist_ok=True)
        oil.to_file(folder.joinpath(f'{py_json["oil_id"]}.json'))


def _add_datafiles(settings):
    """
    The default settings include only the MongoDB connection
    so we need to add any oil import data files to the settings structure
    """
    _add_oillib_files(settings)
    _add_norway_files(settings)
    _add_ec_files(settings)
    _add_exxon_files(settings)


def _add_oillib_files(settings):
    oillib_files = '\n'.join([os.path.join(data_path, fn)
                              for fn in ('OilLib.txt',)])

    settings['oildb.fm_files'] = oillib_files


def _add_norway_files(settings):
    oillib_files = '\n'.join([os.path.join(data_path, 'norway', fn)
                              for fn in ('OilLibNorway.txt',)])

    settings['oildb.nor_files'] = oillib_files


def _add_ec_files(settings):
    ec_files = '\n'.join([os.path.join(data_path, 'env_canada', fn)
                          for fn in ('opp_data_catalogue_en.csv',)])

    settings['oildb.ec_files'] = ec_files

    eccc_files = '\n'.join([os.path.join(data_path, 'env_canada', fn)
                            for fn in ('Catalogue_of_Crude_Oil_and_'
                                       'Oil_Product_Properties_(1999)'
                                       '-Revised_2022_En.csv',)])

    settings['oildb.eccc_files'] = eccc_files


def _add_exxon_files(settings):
    """
    The exxon files are a bit more tricky than the filemaker and Env
    Canada datafiles.  Rather they are tricky in their own unique way.

    Basically they are scraped from the Exxon website and are basically
    one oil, one file.  But the oil name is not contained inside the file,
    but a listing on the web page.  So we need to create an index of names
    and associated files.  Then we traverse the index.

    So exactly what should be contained in the settings?  I think it should
    be the index file.
    """
    exxon_files = '\n'.join([os.path.join(data_path, 'exxon_assays', fn)
                             for fn in ('index.txt',)])

    settings['oildb.exxon_files'] = exxon_files
