import sys
import os
import io
import logging
from datetime import datetime
from argparse import ArgumentParser

from pymongo.errors import DuplicateKeyError

from oil_database.util.term import TermColor as tc
from oil_database.util.db_connection import connect_mongodb
from oil_database.util.settings import file_settings, default_settings

from oil_database.data_sources.noaa_fm import (OilLibraryCsvFile,
                                               OilLibraryRecordParser,
                                               OilLibraryAttributeMapper)

from oil_database.data_sources.env_canada import (EnvCanadaOilExcelFile,
                                                  EnvCanadaRecordParser,
                                                  EnvCanadaAttributeMapper)

from oil_database.data_sources.exxon_assays import (ExxonDataReader,
                                                    ExxonRecordParser,
                                                    ExxonMapper)


# from oil_database.db_init.validation import oil_record_validation
from oil_database.db_init.labels import link_oil_to_labels
from oil_database.models.oil.validation.validate import validate

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)

# All oil library data files are assumed to be in a common data folder
data_path = os.path.sep.join(__file__.split(os.path.sep)[:-3] + ['data'])


def not_implemented(_settings):
    print('\tImport of this dataset is not implemented!!')


def add_all(settings):
    '''
        Import all valid, available datasets from our menu
        a dataset is valid if it has the full complement of handler classes.
    '''
    for item in menu_items:
        if len(item) == 6:
            (label, config,
             record_cls, reader_cls, parser_cls, mapper_cls) = item
            print('\tPerforming import on dataset: {}'.format(label))

            import_records(settings[config],
                           record_cls, reader_cls, parser_cls, mapper_cls)


menu_items = (['NOAA Filemaker', 'oildb.fm_files',
               None,
               OilLibraryCsvFile,
               OilLibraryRecordParser,
               OilLibraryAttributeMapper],
              ['Environment Canada', 'oildb.ec_files',
               None,
               EnvCanadaOilExcelFile,
               EnvCanadaRecordParser,
               EnvCanadaAttributeMapper],
              # ('Exxon Assays', add_exxon_records)
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
argp.add_argument('--config', nargs=1,
                  help=('Specify a *.ini file to supply application settings. '
                        'If not specified, the default is to use a local '
                        'MongoDB server.'))


def import_db_cmd(argv=sys.argv):
    # Let's give a round of applause to Python 3 for making stderr buffered.
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO)

    args = argp.parse_args(argv[1:])

    if args.config is not None:
        settings = file_settings(args.config)
    else:
        print('Using default settings')
        settings = default_settings()
        _add_datafiles(settings)

    logger.info('connect_mongodb()...')
    client = connect_mongodb(settings)

    init_menu_item_collections(client, settings)

    if args.all:
        try:
            add_all(settings)
        except Exception:
            print("{0}() FAILED\n".format(add_all.__name__))
            raise
        exit(0)

    try:
        import_db(settings)
    except Exception:
        print("{0}() FAILED\n".format(import_db.__name__))
        raise


def import_db(settings):
    '''
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

    '''
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
                               reader_cls, parser_cls, mapper_cls)
                end = datetime.now()

                print('time elapsed: {}'.format(end - begin))

    print('quitting the import...')


def init_menu_item_collections(client, settings):
    '''
        We will be loading everything into the same collection, so we set
        all items to the same place.
    '''
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


def import_records(config, oil_collection, reader_cls, parser_cls, mapper_cls):
    '''
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
    '''
    for fn in config.split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = reader_cls(fn)

        total_count = 0
        success_count = 0
        error_count = 0
        for record_data in fd.get_records():
            total_count += 1

            try:
                parser_obj = parser_cls(*record_data)

                oil_obj = mapper_cls(parser_obj)

                link_oil_to_labels(oil_obj)

                oil_pyjson = oil_obj.dict()

                validate(oil_pyjson)
                oil_collection.insert_one(oil_pyjson)
            except DuplicateKeyError as e:
                print('Duplicate fields for {}: {}'
                      .format(tc.change(oil_obj.oil_id, 'red'), e))
                error_count += 1
            except ValueError as e:
                print('Value error for {}: {}'
                      .format(tc.change(oil_obj.oil_id, 'red'), e))
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


def _add_datafiles(settings):
    '''
        The default settings include only the MongoDB connection
        so we need to add any oil import data files to the settings structure
    '''
    _add_oillib_files(settings)
    _add_ec_files(settings)
    _add_exxon_files(settings)


def _add_oillib_files(settings):
    oillib_files = '\n'.join([os.path.join(data_path, fn)
                              for fn in ('OilLib.txt',)])

    settings['oildb.fm_files'] = oillib_files


def _add_ec_files(settings):
    ec_files = '\n'.join([os.path.join(data_path, 'env_canada', fn)
                          for fn in ('Physiochemical properties of '
                                     'petroleum products-EN.xlsx',)])

    settings['oildb.ec_files'] = ec_files


def _add_exxon_files(settings):
    '''
        The exxon files are a bit more tricky than the filemaker and Env
        Canada datafiles.  Rather they are tricky in their own unique way.

        Basically they are scraped from the Exxon website and are basically
        one oil, one file.  But the oil name is not contained inside the file,
        but a listing on the web page.  So we need to create an index of names
        and associated files.  Then we traverse the index.

        So exactly what should be contained in the settings?  I think it should
        be the index file.
    '''
    exxon_files = '\n'.join([os.path.join(data_path, 'exxon_assays', fn)
                             for fn in ('index.txt',)])

    settings['oildb.exxon_files'] = exxon_files
