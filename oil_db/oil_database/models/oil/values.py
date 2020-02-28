
"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

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


class ProductType(str):
    _valid_types = ('crude',
                    'refined',
                    'bitumen product',
                    'other')
    _validator = EnumValidator(_valid_types, WARNINGS["W003"], case_insensitive=True)

    def validate(self):
        return self._validator(self)



@dataclass_to_json
@dataclass
class UnittedValue:
    # fixme: could this use the FloatUnit stuff?
    #        it certainly needs more "smarts"
    """
    Data structure to hold a value with a unit

    This accommodates both a single value and a range of values

    There is some complexity here, so everything is optional

    But maybe it would be better to have some validation on creation

    NOTES:
       If there is a value, there should be no min_value or max_value
       If there is only  a min or max, then it is interpreted as
       greater than or less than
    """
    value: float = None
    min_value: float = None
    max_value: float = None
    unit: str = None
    # unit_type: str = None


@dataclass_to_json
@dataclass
class UnittedRange:
    # fixme: could this use the FloatUnit stuff?
    #        it certainly needs more "smarts"
    """
    Data structure to hold a range of values with a unit

    This differs from UnittedValue in that it Always is a range
    with no single value option

    """
    min_value: float = None
    max_value: float = None
    unit: str = None



@dataclass_to_json
@dataclass
class Density:
    # NOTE: should the values be optional?
    density: UnittedValue = None
    ref_temp: UnittedValue = None
    standard_deviation: float = None
    replicates: int = None
    method: str = None


class DensityList(JSON_List):
    item_type = Density


@dataclass_to_json
@dataclass
class Viscosity:
    viscosity: UnittedValue = None
    ref_temp: UnittedValue = None
    standard_deviation: float = None
    replicates: int = None
    method: str = None


class ViscosityList(JSON_List):
    item_type = Viscosity

@dataclass_to_json
@dataclass
class DistCut:
    fraction: UnittedValue = None
    vapor_temp: UnittedValue = None


class DistCutsList(JSON_List):
    """
    needs some refactoring: should be method, for one
    """
    item_type = DistCut

    def validate(self):
        # do validation here
        pass


