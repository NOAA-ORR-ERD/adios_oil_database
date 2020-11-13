
"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.validators import EnumValidator
from .validation.warnings import WARNINGS


PRODUCT_TYPES = ('Crude Oil, NOS',
                 'Condensate',
                 'Bitumen Blend',
                 'Refined Product, NOS',
                 'Fuel Oil, NOS',
                 'Distillate Fuel Oil',
                 'Petroleum-Derived Solvent',
                 'Residual Fuel Oil',
                 'Bio-Petroleum Fuel Blend',
                 'Bio Fuel Oil',
                 'Lube Oil',
                 'Refinery Intermediate',
                 'Natural Plant Oil',
                 'Dielectric Oil',
                 'Other'
                 )


class ProductType(str):
    _valid_types = PRODUCT_TYPES
    _validator = EnumValidator(_valid_types,
                               WARNINGS["W003"],
                               case_insensitive=True)

    @classmethod
    def validate(cls, value):
        if not value:
            return [WARNINGS["W002"]]
        return cls._validator(value)
