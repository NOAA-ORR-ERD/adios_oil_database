
"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import dataclass_to_json
from ..common.validators import EnumValidator

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS

from dataclasses import dataclass


class ProductType(str):
    _valid_types = ('crude',
                    'refined',
                    'bitumen product',
                    'other')
    _validator = EnumValidator(_valid_types,
                               WARNINGS["W003"],
                               case_insensitive=True)

    def validate(self):
        return self._validator(self)


@dataclass_to_json
@dataclass
class Reference:
    year: int = None
    reference: str = ""
