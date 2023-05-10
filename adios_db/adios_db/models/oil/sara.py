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
        create a Sara object from the data provided

        must be a 4-sequence:

        :param data: [saturate_fraction, aromatic_fraction, resin_fraction, asphaltene_fraction]
                     (any value can be None)

        :param unit: unit -- must be mass fraction, e.g. 'fraction', "%"

        """
        print("in sara.from_data", data, unit)
        sara = cls()
        for field, value in zip(("saturates", "aromatics", "resins", "asphaltenes"), data):
            if value is not None:
                setattr(sara, field, MassFraction(value, unit))
        return sara



