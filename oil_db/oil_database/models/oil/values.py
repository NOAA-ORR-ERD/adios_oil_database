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
    # should a unit be required? or is that a validation thing?
    """
    Data structure to hold a value with a unit
    """
    value: float
    unit: str

@dataclass_to_json
@dataclass
class UnittedRange:
    """
    Data structure to hold a range of values with a unit
    """
    min_value: float = None
    max_value: float = None
    unit: str = ""


@dataclass_to_json
@dataclass
class Viscosity:
    """
    class to hold viscosity data records
    """
    viscosity: UnittedValue
    ref_temp: UnittedValue
    standard_deviation: float = None
    replicates: int = None
    method: str = None


