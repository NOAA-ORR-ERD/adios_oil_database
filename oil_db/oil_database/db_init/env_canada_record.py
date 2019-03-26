#
# This is where we handle the initialization of oil record objects that come
# from the Environment Canada oil properties spreadsheet.
#
import sys
import logging

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from oil_database.util.term import TermColor as tc
from oil_database.data_sources.env_canada import (EnvCanadaOilExcelFile,
                                                  EnvCanadaRecordParser)
from oil_database.models.ec_imported_rec import ECImportedRecord

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def add_ec_records(settings):
    '''
        Add the records from the Environment Canada Excel spreadsheet
        of oil properties.
    '''
    for fn in settings['oillib.ec_files'].split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = EnvCanadaOilExcelFile(fn)

        print('Adding new records to database')

        rowcount = 0
        for record_data in fd.get_records():
            parser = EnvCanadaRecordParser(*record_data)

            try:
                add_ec_record(parser)
            except ValidationError as e:
                print ('validation failed for {}: {}'
                       .format(tc.change(parser.oil_id, 'red'), e))
            except DuplicateKeyError as e:
                print ('duplicate fields for {}: {}'
                       .format(tc.change(parser.oil_id, 'red'), e))

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print('finished!!!  {0} rows processed.'.format(rowcount))


def add_ec_record(parser):
    '''
        Add an Environment Canada Record
    '''
    debug = False
    if debug:
        print ('\nparser.oil_id: {}, parser.name: {}'
               .format(parser.oil_id, parser.name))

        print 'parser.dvis: '
        pp.pprint(parser.dvis)

    model_rec = ECImportedRecord.from_record_parser(parser)

    if debug:
        print 'rec.dvis: '
        for i in model_rec.dvis:
            print '\t', i

    model_rec.save()
