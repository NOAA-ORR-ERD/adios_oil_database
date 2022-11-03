"""
Model class definitions for SARA fractions
"""
from dataclasses import dataclass

from ..common.utilities import dataclass_to_json

from ..common.measurement import MassFraction


@dataclass_to_json
@dataclass
class Sara:
    method: str = None

    saturates: MassFraction = None
    aromatics: MassFraction = None
    resins: MassFraction = None
    asphaltenes: MassFraction = None
