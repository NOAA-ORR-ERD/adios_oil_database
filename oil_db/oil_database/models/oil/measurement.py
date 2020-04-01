
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
class MeasurementBase:
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

    unit_type = None

    def convert_to(self, new_unit):
        for a, v in zip(('value', 'min_value', 'max_value'),
                        (self.value, self.min_value, self.max_value)):
            if v is not None:
                setattr(self, a,
                        convert(self.unit_type,
                                self.convert_from,
                                self.unit,
                                v)
                        )


class Length(MeasurementBase):
    unit_type = "length"


class Temperature(MeasurementBase):
    unit_type = "temperature"
