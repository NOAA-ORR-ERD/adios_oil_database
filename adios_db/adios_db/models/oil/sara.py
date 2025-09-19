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

    @classmethod
    def from_data(cls, data, unit):
        """
        Create a Sara object from the data provided

        Must be a length-4 Sequence (list) -- all in the same units.
         - Any data missing can be set to None

        :param data: [saturate_fraction, aromatic_fraction, resin_fraction, asphaltene_fraction]
                     (any value can be None)

        :param unit: unit -- must be mass fraction, e.g. 'fraction', "%"

        """
        sara = cls()
        for field, value in zip(("saturates", "aromatics", "resins", "asphaltenes"), data):
            if value is not None:
                setattr(sara, field, MassFraction(value, unit))
        return sara

    def __bool__(self):
        return not (self.saturates is None
                    and self.aromatics is None
                    and self.resins is None
                    and self.asphaltenes is None)
