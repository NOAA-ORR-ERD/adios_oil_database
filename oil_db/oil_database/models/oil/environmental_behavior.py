"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from .measurement import DispersibilityList, EmulsionList


@dataclass_to_json
@dataclass
class EnvironmentalBehavior:
    dispersibilities: DispersibilityList = field(default_factory=DispersibilityList)
    emulsions: EmulsionList = field(default_factory=EmulsionList)
