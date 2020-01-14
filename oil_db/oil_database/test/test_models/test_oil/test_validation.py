"""
tests of the validation code
"""

import pytest

from oil_database.models.oil.validation import validate


@pytest.fixture
def no_type_oil():
    no_type_oil = {"name": "Just a Name to Have a Placeholder"}
    return no_type_oil


def test_no_type(no_type_oil):
    validate(no_type_oil)

    assert 'W001: Record has no product type' in no_type_oil["status"]


def test_bad_type(no_type_oil):
    no_type_oil['product_type'] = "Fred"
    validate(no_type_oil)

    print(no_type_oil["status"])
    assert "W002: Record has no product type. Options are: ('crude', 'refined', 'bitumen product', 'other')" in no_type_oil["status"]


def test_correct_type(no_type_oil):
    no_type_oil['product_type'] = "Crude"
    validate(no_type_oil)

    print(no_type_oil["status"])
    for msg in no_type_oil["status"]:
        assert not msg.startswith("W001")
        assert not msg.startswith("W002")
