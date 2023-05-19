#!/usr/bin/env python
import logging

from ..v2.reader import EnvCanadaCsvFile

logger = logging.getLogger(__name__)


class EnvCanadaCsvFile1999(EnvCanadaCsvFile):
    """
    A file reader for the Env. Canada .csv flat data file referencing the data
    from the year 1999.  This is reasonably similar to the previous data set
    we received from them, but some of the columns are different and there are
    some minor differences in the data.

    The name of the file is:
    Catalogue_of_Crude_Oil_and_Oil_Product_Properties_(1999)-Revised_2022_En.csv

    - The fields are comma separated ','.  This may prove to be problematic,
      as some fields, notably the reference field, could contain commmas as
      well.

    - Each row represents a single measurement

    - There are a number of reference fields, i.e. fields that associate
      a particular measurement to an oil.  They are:

        - oil_id: ID of an oil record.  This appears to be the camelcase
                  name of the oil joined by an underscore with its oil ID.
        - oil_index: ECCC ID of an oil record with one or more sub-samples.
                     This is similar to the ests field of the other data set.

    - There are also a number of fields that would not normally be used to
      link a measurement to an oil, but are clearly oil general
      properties.

        - oil_name
        - referenceID
        - reference
        - sample_reference
        - comments
        - origin
        - synonyms

    - There are a number of fields that would intuitively seem to
      be used to link a measurement to a sub-sample

        - index_id: ID of an oil sample.  This appears to be the concatenation
                       of the oil_index and a sample number separated by a
                       period ".".
        - weathering_fraction: This appears to be a percentage value in the
                               range 0-100.
        - grade

    - And finally, we have a set of fields that are used uniquely for the
      measurement

        - property_name
        - property_group
        - property_id
        - value
        - value_id
        - unit_of_measure
        - temperature
        - condition_of_analysis
        - note

    """
    number_of_columns = 22
    oil_id_field_name = 'oil_index'

    def __init__(self, name, encoding='utf-8', **kwargs):
        super().__init__(name, encoding=encoding, **kwargs)
