#!/usr/bin/env python
import logging

from adios_db.models.oil.oil import Oil
from adios_db.data_sources.mapper import MapperBase


logger = logging.getLogger(__name__)


class EnvCanadaCsvRecordMapper(MapperBase):
    '''
        A translation/conversion layer for the Environment Canada imported
        record object.
        Basically, the parser has already got the structure mostly in order,
        but because of the nature of the .csv measurement rows, some re-mapping
        will be necessary to put it in a form that the Oil object expects.
    '''
    def __init__(self, record):
        '''
            :param record: A parsed object representing a single oil or
                           refined product.
            :type record: A record parser object.
        '''
        if hasattr(record, 'oil_obj'):
            self.record = record.oil_obj
        else:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'invalid parser passed in')

    @property
    def oil_id(self):
        return self.record['oil_id']

    def py_json(self):
        rec = Oil.from_py_json(self.record)

        return rec.py_json()
