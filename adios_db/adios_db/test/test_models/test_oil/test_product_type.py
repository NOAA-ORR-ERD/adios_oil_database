"""
tests for the product type model
"""
from pathlib import Path

import pytest

from adios_db.models.oil.product_type import (ProductType,
                                              PRODUCT_TYPES,
                                              types_to_labels,
                                              load_from_csv_file)

product_types_lower = [pt.lower() for pt in PRODUCT_TYPES]

example_file = Path(__file__).parent / "example_products.csv"


@pytest.mark.parametrize("product_type",
                         tuple(product_types_lower) + tuple(PRODUCT_TYPES))
def test_ProductType_validation(product_type):
    pt = ProductType(product_type)

    assert pt.validate(pt) == []


@pytest.mark.parametrize("product_type", ('Crud Oil, NOS',
                                          'Residual Fuel Oils',
                                          'Refinery Interminal',
                                          'Natural Planting Oil',
                                          'Others'
                                          ))
def test_ProductType_validation_invalid(product_type):
    pt = ProductType(product_type)

    result = pt.validate(pt)
    assert len(result) == 1
    assert result[0].startswith("W003:")


def test_load_from_csv_file():
    """
    tests loading the product types and labels from a CSV file
    """
    mapping = load_from_csv_file(example_file)

    assert list(mapping.keys()) == ['Crude Oil NOS', 'Condensate',
                                    'Bitumen Blend']
    assert mapping['Crude Oil NOS'] == {'Light Crude',
                                        'Tight Oil',
                                        'Crude Oil',
                                        'Medium Crude',
                                        'Group V',
                                        'Heavy Crude',
                                        'Bitumen Blend'}


# we are no longer adding all the product types to the labels
# def test_product_types_labels():
#     """
#     checks that all the product types are listed in the labels

#     This is using the data loaded in the module
#     """

#     print(types_to_labels.labels.keys())

#     for pt, labels in types_to_labels.labels.items():
#         assert pt in labels
