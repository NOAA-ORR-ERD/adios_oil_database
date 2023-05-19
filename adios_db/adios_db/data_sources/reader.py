#!/usr/bin/env python
"""
Base classes for various different readers that we may want to use.
"""
import logging
import csv
from builtins import isinstance

logger = logging.getLogger(__name__)


class CsvFile:
    """
    A generalized file reader for comma separated variables (.csv)
    flat datafiles.
    In spite of its name, this type of file can have various different
    separating characters besides commas for its rows and fields.
    """
    def __init__(self, name, field_delim=',', encoding='mac_roman'):
        """
        :param name: The name of the oil library import file
        :type name: A path as a string or unicode

        :param field_delim=',': The character to be used as a tabular
                                field delimiter.
        :type field_delim: A string or unicode
        """
        self.name = name

        self.fileobj = open(name, 'r', encoding=encoding)
        self.reader = csv.DictReader(self.fileobj, delimiter=field_delim)

        self.init_field_names()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.fileobj.close()

    def init_field_names(self):
        next(self.reader)
        self.field_names = self.reader.fieldnames
        self.rewind()

    def readlines(self):
        for row in self.reader:
            yield self.convert_fields(row)

    def readline(self):
        return self.convert_fields(self.reader.__next__())

    def convert_fields(self, row):
        if row is None:
            return None
        elif isinstance(row, dict):
            return {k: self.convert_field(v) for k, v in row.items()}
        else:
            return [self.convert_field(f) for f in row]

    def convert_field(self, field):
        """
        Convert data fields to numeric if possible
        """
        try:
            return int(field)
        except Exception:
            pass

        try:
            return float(field)
        except Exception:
            pass

        if field == '':
            field = None

        return field

    def rewind(self):
        self.fileobj.seek(0)
        self.fileobj.readline()

    def export(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, self.field_names)

            self.rewind()
            for row in self.reader:
                writer.writerow(row)

    def __repr__(self):
        return ("<{}('{}')>".format(self.__class__.__name__, self.name))
