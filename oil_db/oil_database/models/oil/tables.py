"""
classes for managing "tabular" data.

There are a few types:

MultiTempTable: tables of values at temperatures -- as in density and viscosity

StaticTable: table of key:value pairs, where the keys are always the same. e.g. SARA

DynamicTable: table of key value pairs with arbitrary keys. e.g.

"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .values import (UnittedValue,
                     UnittedRange,
                     )


from dataclasses import dataclass, field
from typing import List, Dict


@dataclass_to_json
@dataclass
class DensityMeasurement:
    standard_deviation: float = None
    replicates: int = None
    density: UnittedValue = None
    ref_temp: UnittedValue = None
    method: str = None


@dataclass_to_json
@dataclass
class ViscosityMeasurement:
    standard_deviation: float = None
    replicates: int = None
    viscosity: UnittedValue = None
    ref_temp: UnittedValue = None
    method: str = None


class MultiTempTable:
    """
    Data structure to hold a table of values at multiple temperatures
    e.g. density, viscosity
    """
    def init(self, name):
        self.name = name
        self.rows = []






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


