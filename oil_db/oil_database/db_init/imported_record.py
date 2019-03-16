#
# This is where we handle the initialization of the imported oil record
# objects that come from the Filemaker database.
#
# Basically, we take the parsed record from our OilLib flat file, and
# find a place for all the data.
#
import sys
import logging

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from ..util.term import TermColor as tc
from ..data_sources.oil_library import (OilLibraryCsvFile,
                                        OilLibraryRecordParser)

from ..models.imported_rec import ImportedRecord

logger = logging.getLogger(__name__)


def add_imported_records(settings):
    '''
        Add our imported records from their associated data sources.
        Right now the only data source is the OilLib file.
    '''
    for fn in settings['oillib.files'].split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = OilLibraryCsvFile(fn)
        logger.info('file version: {}'.format(fd.__version__))

        print('Adding new records to database')

        rowcount = 0
        for record_data in fd.get_records():
            parser = OilLibraryRecordParser(*record_data)

            try:
                add_imported_record(parser)
            except ValidationError as e:
                print (u'validation failed for {}: {}'
                       .format(tc.change(parser.adios_oil_id, 'red'), e))
            except DuplicateKeyError as e:
                print (u'duplicate fields for {}: {}'
                       .format(tc.change(parser.adios_oil_id, 'red'), e))

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print('finished!!!  {0} rows processed.'.format(rowcount))


def add_imported_record(parser):
    '''
        Add a record from the NOAA filemaker export flatfile.
    '''
    model_rec = ImportedRecord.from_record_parser(parser)

    model_rec.save()
