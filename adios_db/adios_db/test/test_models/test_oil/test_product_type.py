"""
tests for the product type model
"""
from pathlib import Path

import pytest

from adios_db.models.oil.product_type import (ProductType,
                                              TypeLabelsMap,
                                              PRODUCT_TYPES,
                                              load_from_csv_file)


product_types_lower = [pt.lower() for pt in PRODUCT_TYPES]
example_file = Path(__file__).parent / "example_products.csv"


@pytest.fixture
def example_data():
    return TypeLabelsMap(load_from_csv_file(example_file))


@pytest.mark.parametrize("product_type",
                         tuple(product_types_lower) + tuple(PRODUCT_TYPES))
def test_ProductType_validation(product_type):
    pt = ProductType(product_type)

    assert pt.validate(pt) == []


@pytest.mark.parametrize("product_type", (
    'Crud Oil, NOS',
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


def test_all_labels(example_data):
    labels = example_data.all_labels

    print(labels)
    assert sorted(labels) == sorted([
        'Heavy Crude', 'Crude Oil', 'Tight Oil', 'Light Crude', 'Medium Crude',
        'Group V', 'Bitumen Blend', 'Condensate', 'Refined Product',
        'Refinery Intermediate'
    ])


def test_all_product_types(example_data):
    products = example_data.all_product_types

    assert sorted(products) == sorted([
        'Crude Oil NOS',
        'Condensate',
        'Bitumen Blend'
    ])

@pytest.mark.parametrize(("pt_in", "pt_out"), [
                         ("Crude oil  nos ", "Crude Oil NOS" ),
                         ("Crude Oil  NOS", "Crude Oil NOS" ),
                         ("Condensate", "Condensate" ),
                         (" condensate", "Condensate" ),
                         ("Random junk", "Random junk"),
                         ("", ""),
                         ])
def test_normalize_product_type(pt_in, pt_out):
    pt_norm = ProductType.normalize_product_type(pt_in)

    assert pt_norm == pt_out

