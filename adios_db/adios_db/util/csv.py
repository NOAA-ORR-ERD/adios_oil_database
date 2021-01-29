#!/usr/bin/env python
import logging

logger = logging.getLogger(__name__)


class FileHeaderLengthError(Exception):
    pass


class FileHeaderContentError(Exception):
    pass


class CSVFile(object):
    # FixMe: what does this do that the buil-in csv reader doesn't ??
    '''
    A file reader for flat datafiles in .csv format

    - We will use universal newline support to designate
      a line of text.

    - Each line contains a number of fields separated by a designated
      character. (default ``\t``).  The resulting parsed sequence of lines
      and fields attempts to represent tabular data.
    '''

    def __init__(self, name, field_delim='\t'):
        '''
            :param name: The name of the oil library import file
            :type name: A path as a string or unicode

            :param field_delim='\t': The character to be used as a tabular
                                     field delimiter.
            :type field_delim: A string or unicode
        '''
        self.name = name

        try:
            self.field_delim = field_delim.decode('utf-8')
        except Exception:
            self.field_delim = field_delim

    def __enter__(self):
        '''
            Contextually open our file.  This is compatible with, for ex:

            >>> with CSVFile('myfile.csv') as csv:
            >>>     # file is now open.  Do some stuff with it
            >>>     pass
            >>> # our file is now closed
        '''
        self.fileobj = open(self.name, 'r', errors='surrogatepass')

        return self

    def __exit__(self, *_args):
        '''
            Contextually close our file.
        '''
        self.fileobj.close()

    def _parse_row(self, line):
        '''
            Parse a row of .csv data into a sequence of fields.
            It is assumed that this data will most likely be the results of
            the readline() file function.

            :param line: A row of .csv text data
            :type line: string or unicode
        '''
        if line in ('', b''):
            # readline() returns empty string on EOF and '\n' for empty lines
            return None

        if len(line) > 0:
            try:
                row = line.rstrip('\n')
            except Exception:
                row = line.decode('utf-8').rstrip('\n')

            row = row.split(self.field_delim)

            row = [c.strip('"') for c in row]

            row = [c if len(c) > 0 else None for c in row]
        else:
            # empty line after stripping the newline character
            # means a single null field
            row = [None]

        return row

    def readline(self):
        '''
            Get the next row of .csv data, parsed into a sequence of fields.
        '''
        return self._parse_row(self.fileobj.readline())

    def readlines(self):
        '''
            Iterate over the lines in the .csv file.
        '''
        while True:
            line = self.readline()

            if line is None:
                break
            elif len(line) > 0:
                yield line

    def seek(self, pos):
        self.fileobj.seek(pos)

    def rewind(self):
        self.seek(0)

    def write(self):
        '''
            This is primarily a file reader class.  We don't maintain any
            in-memory data, so it doesn't really make sense to write data
            to the current open file.
        '''
        raise NotImplementedError("Can't write to currently open file")

    def __repr__(self):
        return "<CSVFile('%s')>" % (self.name)


class CSVFileWithHeader(CSVFile):
    '''
        Similar to the CSVFile, but the first row is a header containing
        the names of the columns.
    '''
    def __enter__(self):
        '''
            Contextually open our file.
        '''
        self.fileobj = open(self.name, 'r')
        self._set_table_columns()

        return self

    def __exit__(self, *_args):
        '''
            Contextually close our file.
        '''
        self.fileobj.close()

        self.file_columns = None
        self.file_columns_lu = None
        self.num_columns = None

    def _set_table_columns(self):
        self.file_columns = self.readline(check_row=False)
        self.file_columns_lu = dict(zip(self.file_columns,
                                        range(len(self.file_columns))))
        self.num_columns = len(self.file_columns)

    def _check_row(self, row):
        '''
            check that our row matches the header

            :param line: A row of parsed fields
            :type line: sequence type
        '''
        if row is not None and len(row) != self.num_columns:
            raise FileHeaderLengthError('Bad row data: '
                                        'should match the length of the '
                                        'first row!!')

    def readline(self, check_row=True):
        '''
            Get the next row of .csv data, parsed into a sequence of fields.
        '''
        row = super().readline()

        if check_row is True:
            self._check_row(row)

        return row

    def rewind(self):
        super().rewind()

        self.readline(check_row=False)
