"""
tests of the validation code

most need to be updated to test validating an Oil object directly
"""

import pytest
import json
from pathlib import Path
import copy

from oil_database.models.oil.oil import Oil
from oil_database.models.oil.validation.validate import (validate_json,
                                                         validate)


HERE = Path(__file__).parent

# NOTE: this should be updated when the data model is updated.
BIG_RECORD = json.load(open(
    HERE.parent / "ExampleFullRecord.json"
))


@pytest.fixture
def big_record():
    return Oil.from_py_json(BIG_RECORD)


@pytest.fixture
def no_type_oil():
    no_type_oil = {'oil_id': 'AD00123',
                   'metadata': {'name': 'An oil name'}
                   }
    return Oil.from_py_json(no_type_oil)


def snippet_in_oil_status(snippet, oil):
    """
    checks if the particular snippet in one of the messages
    """
    for msg in oil.status:
        if snippet in msg:
            return True
    return False


def snippet_not_in_oil_status(snippet, oil):
    """
    checks if the particular snippet in one of the messages
    """
    return not snippet_in_oil_status(snippet, oil)


def test_no_id():
    """
    should get a particular ValueError if you try an invalid dict
    """
    try:
        validate_json({"this": 3})
    except TypeError as err:
        assert ("E001: Record has no oil_id: every record must have an ID"
                in str(err))


@pytest.mark.parametrize("name", ["  ",
                                  "X",
                                  "4",
                                  "this"
                                  ])

def test_reasonable_name(name):
    # unreasonable names should fail
    oil = Oil(oil_id='AD00123')
    oil.metadata.name = name
    validate(oil)

    assert snippet_in_oil_status("W001:", oil)


def test_no_type(no_type_oil):
    validate(no_type_oil)

    assert snippet_in_oil_status("W002:", no_type_oil)


def test_bad_type(no_type_oil):
    no_type_oil.metadata.product_type = "Fred"
    validate(no_type_oil)

    assert snippet_in_oil_status("W003:", no_type_oil)


def test_correct_type(no_type_oil):
    no_type_oil.metadata.product_type = "Crude"
    validate(no_type_oil)

    print(no_type_oil.status)
    for msg in no_type_oil.status:
        assert not msg.startswith("W001")
        assert not msg.startswith("W002")


def test_big_record_no_type(big_record):
    """
    remove the product type from the record
    """
    oil = big_record
    oil.metadata.product_type = None

    validate(oil)

    print(oil.status)

    assert snippet_in_oil_status("W002", oil)


def test_no_api_crude(no_type_oil):
    oil = no_type_oil
    oil.metadata.product_type = "Crude"
    validate(oil)
    assert snippet_in_oil_status("E002:", oil)


def test_no_api_not_crude(no_type_oil):
    oil = no_type_oil
    oil.metadata.product_type = "Refined"
    validate(oil)
    assert snippet_in_oil_status("W004:", oil)


def test_api_outragious(no_type_oil):
    oil = no_type_oil
    oil.metadata.API = -200
    validate(oil)
    assert snippet_in_oil_status("W005:", oil)


def test_no_subsamples(no_type_oil):
    oil = no_type_oil
    validate(oil)
    assert snippet_in_oil_status("E003", oil)


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


def test_distillation_cuts(big_record):
    oil = big_record

    validate(oil)

    assert snippet_not_in_oil_status("W007:", oil)


def test_no_distillation_cuts(big_record):
    oil = big_record

    # remove the cut data
    oil.sub_samples[0].distillation_data = []
    validate(oil)
    print(oil.status)

    assert snippet_in_oil_status("W007:", oil)


