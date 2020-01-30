"""
tests of the validation code
"""

import pytest
import json
from pathlib import Path
import copy

from oil_database.models.oil.validation import validate

BIG_RECORD = json.load(open(Path(__file__).parent / "ExampleBigRecord_pp.json"))


@pytest.fixture
def big_record():
    return copy.deepcopy(BIG_RECORD)


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


def test_big_record(big_record):
    """
    making sure that this works with a pretty complete record

    all this tests is that it doesn't barf
    """
    validate(big_record)

    print(big_record["status"])


def test_big_record_no_type(big_record):
    """
    remove the product type from the record
    """
    big_record['product_type'] = None

    validate(big_record)

    print(big_record["status"])
    for msg in big_record["status"]:
        if msg.startswith("W001"):
            break
    else:
        assert False

    assert True

