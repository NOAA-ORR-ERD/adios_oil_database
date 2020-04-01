
"""
classes for holding a measurement
"""

from unit_conversion import convert

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )
from ..common.validators import (EnumValidator,
                                 )

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass_to_json
@dataclass
class MeasurementDataclass:
    """
    Data structure to hold a value with a unit

    This accommodates both a single value and a range of values

    There is some complexity here, so everything is optional

    But maybe it would be better to have some validation on creation

    NOTES:
       If there is a value, there should be no min_value or max_value
       If there is only  a min or max, then it is interpreted as
       greater than or less than

       There needs to be validation on that!
    """
    value: float = None
    unit: str = None
    min_value: float = None
    max_value: float = None
    standard_deviation: float = None
    replicates: float = None


class MeasurementBase(MeasurementDataclass):
    # need to add these here, so they won't be overwritten by the
    # decorator
    unit_type = None

    def py_json(self, sparse=True):
        # unit_type is added here, as it's not a settable field
        print("py_json called")
        pj = super().py_json(sparse)
        print(pj)
        pj['unit_type'] = self.unit_type
        return pj

    # def convert_to(self, new_unit):
    #     for a, v in zip(('value', 'min_value', 'max_value', 'standard_deviation'),
    #                     (self.value, self.min_value, self.max_value, self.standard_deviation)):
    #         if v is not None:
    #             setattr(self, a,
    #                     convert(self.unit_type,
    #                             self.unit,
    #                             new_unit,
    #                             v)
    #                     )
    #         self.unit = new_unit

    def convert_to(self, new_unit):
        for attr in ('value', 'min_value', 'max_value', 'standard_deviation'):
            val = getattr(self, attr)
            if val is not None:
                new_val = convert(self.unit_type,
                                  self.unit,
                                  new_unit,
                                  val)
                setattr(self,
                        attr,
                        new_val
                        )
        self.unit = new_unit



class Length(MeasurementBase):
    unit_type = "length"


class Temperature(MeasurementBase):
    unit_type = "temperature"
    def __init__(self):
        raise NotImplementedError("Need to special case standard deviation: it's not absolute")
