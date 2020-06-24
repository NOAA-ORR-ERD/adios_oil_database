#!/usr/bin/env python
import sys
from datetime import datetime
import logging
from itertools import zip_longest

from dateutil import parser

logger = logging.getLogger(__name__)


class ImportFileHeaderLengthError(Exception):
    pass


class ImportFileHeaderContentError(Exception):
    pass


class OilLibraryCsvFile:
    ''' A specialized file reader for the OilLib and CustLib
        flat datafiles.
        - We will use universal newline support to designate
          a line of text.
        - Additionally, each line contains a number of fields
          separated by a tab ('\t').  In this way it attempts
          to represent tabular data.
        - The first line in the file contains a file format
          version number ('N.N'), followed by a date ('d/m/YY'),
          and finally the product ('adios').
        - The second line in the file contains a table header,
          where each field represents the "long" name of a
          tabular column.
        - The rest of the lines in the file contain table data.

        TODO: I just noticed that we are not making use of the .csv utility
              class.  We need to refactor this to use it.
    '''
    def __init__(self, name, field_delim='\t', ignore_version=False):
        '''
            :param name: The name of the oil library import file
            :type name: A path as a string or unicode

            :param field_delim='\t': The character to be used as a tabular
                                     field delimiter.
            :type field_delim: A string or unicode

            :param ignore_version=False: Ignore the exceptions generated by a
                                         failure to parse the version header
                                         in the file.
                                         Normally we want to simply fail in
                                         this case, but for diagnosing the
                                         content of new or unfamiliar import
                                         files, we can continue on in an
                                         attempt to build our object.
            :type ignore_version: Boolean
        '''
        self.name = name
        self.file_columns = None
        self.file_columns_lu = None
        self.num_columns = None
        self._row_lu = {}

        self.fileobj = open(name, 'r', encoding='mac_roman')
        self.field_delim = field_delim

        self.__version__ = self.readline(cache=False)
        print('file version: ', self.__version__)
        self._check_version_hdr(ignore_version)

        self._set_table_columns()

    def _check_version_hdr(self, ignore_version):
        '''
            Check that the file has a proper header.  Right now we are just
            checking for adios specific fields.
        '''
        if len(self.__version__) != 3:
            if ignore_version:
                # If we failed on header length, it is likely we have a
                # missing header.  If so, we probably read the column names
                # instead.  So we need to undo our readline() if we are
                # ignoring this.
                self.__version__ = None
                self.fileobj.seek(0)
            else:
                raise ImportFileHeaderLengthError('Bad file header: '
                                                  'did not find '
                                                  '3 fields for version!!')
        elif not self.__version__[-1].startswith('adios'):
            if ignore_version:
                # If we failed on header content, we probably have a bad
                # or unexpected header, but a header nonetheless.
                pass
            else:
                raise ImportFileHeaderContentError('Bad file header: '
                                                   'did not find '
                                                   'product field!!')

    def _set_table_columns(self):
        self.file_columns = self.readline(cache=False)
        self.file_columns_lu = dict(zip(self.file_columns,
                                        range(len(self.file_columns))))
        self.num_columns = len(self.file_columns)

    def _parse_row(self, line):
        if line == '':
            # readline() returns empty string on EOF and '\n' for empty lines
            return None

        line = line.strip()
        if len(line) > 0:
            row = (line.split(self.field_delim))
            row = [c.strip('"') for c in row]
            row = [c if len(c) > 0 else None for c in row]
        else:
            row = []
        return row

    def get_records(self):
        '''
            This is the API that the oil import processes expect
        '''
        for r in self.readlines():
            if len(r) < 10:
                logger.info('got record: {}'.format(r))

            yield [dict(zip_longest(self.file_columns, r)),
                   self.file_props]

    def get_record(self, oil_id):
        if len(self._row_lu) == 0:
            list(self.get_records())

        return [dict(zip_longest(self.file_columns, self._row_lu[oil_id])),
                self.file_props]

    def readlines(self):
        while True:
            line = self.readline()

            if line is None:
                break
            elif len(line) > 0:
                yield line

    def readline(self, cache=True):
        row = self.convert_fields(self._parse_row(self.fileobj.readline()))

        if cache and row is not None:
            oil_id = row[self.file_columns_lu['ADIOS_Oil_ID']]
            self._row_lu[oil_id] = row

        return row

    def convert_fields(self, row):
        if row is None:
            return None
        else:
            return [self.convert_field(f) for f in row]

    def convert_field(self, field):
        '''
            Convert data fields to numeric if possible
        '''
        try:
            return int(field)
        except Exception:
            pass

        try:
            return float(field)
        except Exception:
            pass

        return field

    def rewind(self):
        self.fileobj.seek(0)
        first_line = self.readline()

        if (self.__version__ is not None and
                len(first_line) == len(self.__version__)):
            logger.debug('first line contains the version header')
            self.readline()
        elif len(first_line) == len(self.file_columns):
            # For tabular data, the number of data fields should be the same
            # as the column names, so this check will not be able to tell
            # if the column names are missing.
            # But at this point, we have already opened the file and
            # constructed our object and performed as many reasonable checks
            # as we can.  So we just try to be consistent with that.
            logger.debug('first line contains the file column names')
        else:
            raise ImportFileHeaderLengthError('Bad file header: '
                                              'should have found either '
                                              'the version or field names '
                                              'in the first row!!')

    def export(self, filename):
        self.rewind()

        file_out = open(filename, 'w')

        if self.__version__ is not None:
            logger.debug(self.field_delim.join(self.__version__))

            file_out.write(self.field_delim.join(self.__version__))
            file_out.write('\n')

        file_out.write(self.field_delim.join(self.file_columns))
        file_out.write('\n')

        for line in self.readlines():
            line = ['' if f is None else f
                    for f in line]

            sys.stderr.write('.')
            file_out.write(self.field_delim.join(line))
            file_out.write('\n')

        file_out.close()

    @property
    def file_props(self):
        version, created, app = self.__version__

        created_date = parser.parse(created,
                                    default=datetime(1970, 1, 1, 0, 0))

        return {'version': version,
                'created': created_date,
                'application': app}

    def __repr__(self):
        return ("<{}('{}')>".format(self.__class__.__name__, self.name))
