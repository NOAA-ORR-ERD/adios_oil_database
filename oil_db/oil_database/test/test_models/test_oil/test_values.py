
import pytest

from oil_database.models.oil.values import (ProductType,
                                            Reference,
                                            PRODUCT_TYPES,
                                            )

product_types_lower = [pt.lower() for pt in PRODUCT_TYPES]


@pytest.mark.parametrize("product_type", tuple(product_types_lower))
def test_ProductType_validation(product_type):
    pt = ProductType(product_type)

    assert pt.validate() == []


@pytest.mark.parametrize("product_type", ('Crud Oil, NOS',
                                          'Residual Fuel Oils',
                                          'Refinery Interminal',
                                          'Natural Planting Oil',
                                          'Others'
                                          ))
def test_ProductType_validation_invalid(product_type):
    pt = ProductType(product_type)

    result = pt.validate()
    assert len(result) == 1
    assert result[0].startswith("W003:")


def test_Reference():
    ref = Reference(year=2013)
    ref.reference = ('Barker, C.H. 2013. "An Arbitrary Title". Journal '
                     'of Nonsense.Seattle, WA. Vol. 13 No. 3 pp. 123-125')

    assert ref.year == 2013


def test_Reference_json():
    ref = Reference(year=2013)
    ref.reference = ('Barker, C.H. 2013. "An Arbitrary Title". Journal '
                     'of Nonsense.Seattle, WA. Vol. 13 No. 3 pp. 123-125')

    py_json = ref.py_json()

    assert py_json['year'] == 2013

    ref2 = Reference.from_py_json(py_json)

    assert ref2.year == 2013
    assert "Barker, C.H." in ref2.reference

    assert ref == ref2
