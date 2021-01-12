
"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from pathlib import Path
import csv

from ...util.many_many import ManyMany
from ..common.validators import EnumValidator
from .validation.warnings import WARNINGS

# this is now loaded from a file -- see end of this module

# PRODUCT_TYPES = ('Crude Oil, NOS',
#                  'Condensate',
#                  'Bitumen Blend',
#                  'Refined Product, NOS',
#                  'Fuel Oil, NOS',
#                  'Distillate Fuel Oil',
#                  'Petroleum-Derived Solvent',
#                  'Residual Fuel Oil',
#                  'Bio-Petroleum Fuel Blend',
#                  'Bio Fuel Oil',
#                  'Lube Oil',
#                  'Refinery Intermediate',
#                  'Natural Plant Oil',
#                  'Dielectric Oil',
#                  'Other'
#                  )

def load_from_csv_file(filepath=None):
    """
    Loads the product types and labels mapping from a CSV file

    :param filepath=None: The name of the file to load from. If not
                          provided, it will look for:
                          "product_types_and_labels.csv" next to this module

    """

    if filepath is None:
        filepath = Path(__file__).parent / "product_types_and_labels.csv"

    with open(filepath, newline='') as csvfile:
        # skip the header:
        while True:
            line = csvfile.readline()
            if line.strip().startswith("DATA TABLE:"):
                break

        ptypes_labels = {}
        reader = csv.reader(csvfile, dialect='excel')
        labels = next(reader)[2:]
        for row in reader:
            pt = row[0]
            for i, val in enumerate(row[2:]):
                if val.strip():
                    ptypes_labels.setdefault(pt, set()).add(labels[i])
        return ptypes_labels


PRODUCT_TYPE_LABEL_MAPPING = load_from_csv_file()
PRODUCT_TYPES = tuple(PRODUCT_TYPE_LABEL_MAPPING)

types_to_labels = ManyMany(PRODUCT_TYPE_LABEL_MAPPING)


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






