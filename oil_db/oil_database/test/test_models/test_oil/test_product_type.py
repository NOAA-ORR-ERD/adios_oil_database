
import pytest

from oil_database.models.oil.product_type import (ProductType,
                                                  PRODUCT_TYPES,
                                                  )

product_types_lower = [pt.lower() for pt in PRODUCT_TYPES]


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

