"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass_to_json
@dataclass
class UnittedValue:
    # fixme: could this use the FloatUnit stuff?
    """
    Data structure to hold a value with a unit

    This accommodates both a single value and a range of values

    There is some complexity here, so everything is optional

    But maybe it would be better to have some validation on creation
    """
    value: float = None
    min_value: float = None
    max_value: float = None
    unit: str = None



# @dataclass_to_json
# @dataclass
# class UnittedRange:
#     """
#     Data structure to hold a range of values with a unit
#     """
#     min_value: float = None
#     max_value: float = None
#     unit: str = ""


@dataclass_to_json
@dataclass
class Density:
    # NOTE: should the values be optional?
    density: UnittedValue = None
    ref_temp: UnittedValue = None
    standard_deviation: float = None
    replicates: int = None
    method: str = None


@dataclass_to_json
@dataclass
class Viscosity:
    viscosity: UnittedValue = None
    ref_temp: UnittedValue = None
    standard_deviation: float = None
    replicates: int = None
    method: str = None

