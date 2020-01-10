"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .values import UnittedValue, Density, Viscosity

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass_to_json
@dataclass
class Sample:
    """
    represents the physical and chemical properties of particular sub sample.

    could be fresh oil, or weathered samples, or distillation cuts, or ...
    """
    # metadata:
    name: str = "Fresh, Unweathered Oil"
    short_name: str = "Fresh"
    fraction_weathered: float = None
    boiling_point_range: tuple = None

    # from Exxon Dist cut data
    cut_volume: UnittedValue = None

    # should we use unit types here?
    densities: List[Density] = field(default_factory=list)
    kvis: List[Viscosity] = field(default_factory=list)
    dvis: List[Viscosity] = field(default_factory=list)



def list_of_samples():
    """
    create a list with one sample -- to use as a factory function
    """
    return JSON_List([Sample()])
