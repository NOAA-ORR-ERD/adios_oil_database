#!/usr/bin/env python
from os.path import basename
import logging
from collections import defaultdict

from openpyxl import load_workbook

from adios_db.util import sigfigs, strip

logger = logging.getLogger(__name__)


class EnvCanadaOilExcelFile(object):
    """
    A specialized file reader for the Environment Canada oil spreadsheet.

    - This is an Excel spreadsheet with an .xlsx extension.  We can use
      the third party openpyxl package to reach the content.

    - The first column in the file contains the names of oil property
      categories.

    - The second column in the file contains the names of specific oil
      properties.

    - The rest of the columns in the file contain oil property values.
    """
    def __init__(self, name):
        """
        :param name: The name of the oil library import file
        :type name: A path as a string or unicode
        """
        self.name = name

        self.wb = load_workbook(self.name, data_only=True)

        self.file_props = dict([(e, getattr(self.wb.properties, e))
                                for e in self.wb.properties.__elements__])
        self.file_props['name'] = basename(name)

        self.db_sheet = self.wb['Database']

        self.col_indexes = self._get_oil_column_indexes()
        self.field_indexes = self._get_row_field_names()
        self._conditions = None

    def _get_oil_column_indexes(self):
        """
        This is tailored to parse the data format of the Excel spreadsheet
        of oil properties by Environment Canada (2017).
        link: https://open.canada.ca/data/en/dataset?q=petroleum+products

        - A single oil can be represented by one or more contiguous
          columns.  They can sometimes be grouped by name, although this
          is not always true, especially with the refined products.
          It seems that the ESTS code is the only reliable way of grouping
          them.
        - The ESTS code is the way they identify the samples they test,
          and it contains two or three numbers separated by a period '.'.
          The first number seems to identify the species of the petroleum
          substance, and the rest identify a degree of weathering,
          either natural or simulated in a laboratory.
        - We will return a dict with oil names as keys and a list of
          associated column indexes as values.

        Note: the April 2020 version of this datasheet has a single oil
              record for which the ESTS code cells have been merged into
              A single cell.  This has created a "gap" cell with a null
              value.  So we need to remember the previous cell value.
        """
        col_headers = defaultdict(list)

        prev_code = None
        for idx, col in enumerate(self.db_sheet.columns):
            if idx >= 5:
                ests_code = col[4].value

                if ests_code is None:
                    ests_code = prev_code
                else:
                    ests_code = str(ests_code).split('.')[0]
                    ests_code = str(int(ests_code))

                col_headers[ests_code].append(idx)

                prev_code = ests_code

        return col_headers

    def _get_row_field_names(self):
        """
        This is tailored to parse the data format of the Excel spreadsheet
        of oil properties that was given to NOAA by Environment Canada
        (2017).

        Column 0 contains field category names in which each single
        category is represented by a contiguous group of rows, and only
        the first row contains the name of the category.

        Within the group of category rows, column 1 contains specific oil
        property names.  So to get a specific property for an oil, one
        needs to reference (category, property)
        A property name within a category is not unique.  For example,
        emulsion at 15C has multiple standard_deviation fields.

        There also exist rows that are not associated with any oil property
        which contain blank fields for both category and property.

        For field names, we would like to keep them lowercase, strip out
        the special characters, and separate the individual word components
        of the field name with '_'
        """
        row_fields = defaultdict(lambda: defaultdict(list))
        row_prev_name = None

        for idx, row in enumerate(self.db_sheet.rows):
            if idx == 0:
                # First row needs to setup the header fields, so we make the
                # first cell an empty field regardless what is actually in
                # there. (The April 2020 update of this file contained a bunch
                # of garbage text)
                row[0].value = None

            if all([(r.value is None) for r in row[:2]]):
                category_name, field_name = None, None
            elif row[0].value is not None:
                category_name = row[0].value.strip()
                row_prev_name = category_name
                if row[1].value is not None:
                    field_name = str(row[1].value).strip()
                else:
                    field_name = None
            else:
                category_name = row_prev_name
                if row[1].value is not None:
                    field_name = str(row[1].value).strip()
                else:
                    field_name = None

            row_fields[category_name][field_name].append(idx)

        return row_fields

    def __repr__(self):
        return "<OilLibraryFile('%s')>" % (self.name)

    def _get_record_raw_columns(self, name):
        """
        Return the columns in the Excel sheet referenced by the name of an
        oil.
        Note: the Excel sheet columns object has no direct indexing,
              only a next().  This is why we are using walk method to get
              our indexed columns.
        Note: It has been decided that we will only keep 5 significant
              digits of any floating point values in the datasheet.
        """
        return list(zip(*[[sigfigs(cell.value, 5) for cell in col]
                          for i, col in enumerate(self.db_sheet.columns)
                          if i in self.col_indexes[name]]))

    def get_records(self):
        """
        Iterate through all the oils, returning all the properties of each one.
        """
        for name in self.col_indexes:
            yield self.get_record(name)

    def get_record(self, name):
        """
        A 'record' coming out of our reader is a dict of dicts
        representing the data for a single oil.

        - The top level keys are the raw category names as seen in the
          first column of the spreadsheet

        - The second level keys are the raw field names that are contained
          within the category, as seen in the second column of the
          spreadsheet

        - Each value in the field dict is a list representing a horizontal
          slice of the columns that comprise the record
        """
        ret = {}
        record_data = self._get_record_raw_columns(name)

        for cat, sub_cat in self.field_indexes.items():
            cat_values = {}

            for f, idxs in sub_cat.items():
                values_i = [record_data[i] for i in idxs]

                if len(idxs) == 1:
                    # flatten the list
                    values_i = [i for sub in values_i for i in sub]
                else:
                    # transpose the list
                    values_i = list(zip(*values_i))

                cat_values[f] = values_i

            ret[cat] = cat_values

        return ret, self.conditions, self.file_props

    @property
    def conditions(self):
        """
        The April 2020 update of the Environment Canada datasheet contained
        a few extra columns that contained data concerning the testing
        conditions for the measurements.

        This information is indexed in the same way as the field data,
        but we only need to create it one time upon opening the file.
        """
        if self._conditions is None:
            ret = {}
            record_data = self._get_conditions_columns()

            for cat, sub_cat in self.field_indexes.items():
                cat_values = {}

                for f, idxs in sub_cat.items():
                    values_i = [record_data[i] for i in idxs]

                    for i, v in enumerate(values_i):
                        unit, ref_temp, condition = v
                        values_i[i] = {
                            'unit': unit,
                            'ref_temp': ref_temp,
                            'condition': condition
                        }

                    if len(values_i) == 1:
                        values_i = values_i[0]

                    cat_values[f] = values_i

                ret[cat] = cat_values

            self._conditions = ret

        return self._conditions

    def _get_conditions_columns(self):
        """
        The April 2020 update of the Environment Canada datasheet contained
        a few extra columns that contained data concerning the testing
        conditions for the measurements. They are:
        - Unit of Measurement: Instead of annotating the category and/or
                               field names with unit information, they
                               put this information into a dedicated column
        - Temperature: Instead of annotating temperature information into
                       the field names, they put this information into a
                       dedicated column.
        - Conditions of analysis: Other significant information concerning
                                  the measurements taken seem to be entered
                                  here.  Most significantly, non-newtonian
                                  shear rate for viscosities.  This was not
                                  there before.
        """
        return list(zip(*[[sigfigs(strip(cell.value), 5) for cell in col]
                          for i, col in enumerate(self.db_sheet.columns)
                          if i in [2, 3, 4]]))
