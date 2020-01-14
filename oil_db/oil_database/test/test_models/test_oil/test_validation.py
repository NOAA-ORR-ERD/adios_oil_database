"""
tests of the validation code
"""

import pytest

from oil_database.models.oil.validation import validate


@pytest.fixture
def no_type_oil():
    no_type_oil = {"name": "Just a Name to Have a Placeholder"}
    return no_type_oil



def test_type(no_type_oil):
    validate(no_type_oil)

    assert no_type_oil["status"] == []