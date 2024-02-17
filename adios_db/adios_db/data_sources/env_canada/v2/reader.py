#!/usr/bin/env python
import logging

from ...reader import CsvFile


logger = logging.getLogger(__name__)


class InvalidFileError(Exception):
    """
    Error trying to open a file that is non-compliant with the Env. Canada
    .csv format.
    """


class EnvCanadaCsvFile(CsvFile):
    """
    A file reader for the Env. Canada .csv (.txt, actually) flat datafile.

    - The original source had a comma separated format with actual commas
      (',') as field separators.  This was insufficient, as some fields,
      notably the reference field, contained commmas in their content.

    - Each row represents a single measurement

    - There are a number of reference fields, i.e. fields that associate
      a particular measurement to an oil.  They are:

        - oil_id: ID of an oil record.  This appears to be the camelcase
                  name of the oil joined by an underscore with the ESTS
                  oil ID.
        - ests: ESTS ID of an oil record with one or more sub-samples

    - There are also a number of fields that would not normally be used to
      link a measurement to an oil, but are clearly oil general
      properties.

        - oil_name
        - date_sample_received
        - source
        - comments
        - reference

    - There are a number of fields that would intuitively seem to
      be used to link a measurement to a sub-sample

        - ests_id: ESTS ID of an oil sample
        - weathering_fraction
        - weathering_percent
        - weathering_method

    - And finally, we have a set of fields that are used uniquely for the
      measurement

        - value_id
        - property_id
        - property_group
        - property_name
        - unit_of_measure
        - temperature
        - condition_of_analysis
        - value
        - standard_deviation
        - replicates
        - method
    """
    number_of_columns = 23
    oil_id_field_name = 'ests'

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        print(f'The number of fields should be {self.number_of_columns} '
              f'and they are {len(self.field_names)}')
        if len(self.field_names) != self.number_of_columns:
            raise InvalidFileError('Fields are invalid for an '
                                   'Environment Canada .csv file')

    def get_records(self):
        """
        This is the API that the oil import processes expect

        A 'record' coming out of our reader is a list of rows representing
        the data for a single oil.
        """
        prev_oil_id = None
        oil_out = []

        for row in self.readlines():
            oil_id = row[self.oil_id_field_name]

            if prev_oil_id is not None and prev_oil_id != oil_id:
                # we have moved on to the next oil
                yield [oil_out]

                oil_out = []

            oil_out.append(row)
            prev_oil_id = oil_id

        if len(oil_out) > 0:
            yield [oil_out]
