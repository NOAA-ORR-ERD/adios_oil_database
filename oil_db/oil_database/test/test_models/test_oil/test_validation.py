"""
tests of the validation code
"""

import pytest
import json
from pathlib import Path
import copy

from oil_database.models.oil.validation import validate

# NOTE: this should be updated when the data model is updated.
BIG_RECORD = json.load(open(Path(__file__).parent / "ExampleBigRecord_pp.json"))


@pytest.fixture
def big_record():
    return copy.deepcopy(BIG_RECORD)


@pytest.fixture
def no_type_oil():
    no_type_oil = {"name": "Just a Name to Have a Placeholder"}
    return no_type_oil


def snippet_in_oil_status(snippet, oil):
    """
    checks if the particular snippet in one of the messages
    """
    for msg in oil["status"]:
        if snippet in msg:
            return True
    return False


def snippet_not_in_oil_status(snippet, oil):
    """
    checks if the particular snippet in one of the messages
    """
    for msg in oil["status"]:
        if snippet in msg:
            return False
    return True


def test_no_name():
    oil = {}
    validate(oil)

    assert "E001: Record has no name: every record must have a name" in oil['status']


@pytest.mark.parametrize("name", ["  ",
                                  "X",
                                  "4",
                                  "this"
                                  ])
def test_reasonable_name(name):
    # unreasonable names should fail
    oil = {"name": name}  # only spaces
    validate(oil)

    assert snippet_in_oil_status("W001:", oil)


def test_no_type(no_type_oil):
    validate(no_type_oil)

    assert snippet_in_oil_status("W002:", no_type_oil)


def test_bad_type(no_type_oil):
    no_type_oil['product_type'] = "Fred"
    validate(no_type_oil)

    print(no_type_oil["status"])
    assert snippet_in_oil_status("W003:", no_type_oil)


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

    assert snippet_in_oil_status("W002", big_record)


def test_no_api_crude(no_type_oil):
    oil = no_type_oil
    oil['product_type'] = "Crude"
    validate(oil)
    assert snippet_in_oil_status("E002:", oil)


def test_no_api_not_crude(no_type_oil):
    oil = no_type_oil
    oil['product_type'] = "Refined"
    validate(oil)
    assert snippet_in_oil_status("W004:", oil)


def test_api_outragious(no_type_oil):
    oil = no_type_oil
    oil['api'] = -200
    validate(oil)
    assert snippet_in_oil_status("W005:", oil)



def test_api_real_record(big_record):
    """
    note that this used a real record as of version 1:

    api is stored in the zeroth subrecord..

    so this makes sure the API tests work with that.
    """
    oil = big_record
    validate(oil)

    assert snippet_not_in_oil_status("E002:", oil)
    assert snippet_not_in_oil_status("W004:", oil)


def test_density_data(big_record):
    oil = big_record

    validate(oil)

    assert snippet_not_in_oil_status("W004:", oil)


def test_no_densities(big_record):
    oil = big_record
    validate(oil)

    assert snippet_not_in_oil_status("W006:", oil)

    assert False

