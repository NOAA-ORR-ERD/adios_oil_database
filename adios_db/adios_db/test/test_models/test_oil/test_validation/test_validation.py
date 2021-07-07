"""
tests of the validation code

most need to be updated to test validating an Oil object directly
"""

import copy
import json
from pathlib import Path
import math
import pytest

import unit_conversion as uc

from adios_db.computation import physical_properties
from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.physical_properties import DensityPoint
from adios_db.models.common.measurement import *
from adios_db.models.oil.validation.validate import (validate_json, validate)

from adios_db.scripting import get_all_records

HERE = Path(__file__).parent

TEST_DATA_DIR = HERE.parent.parent.parent / "data_for_testing" / "noaa-oil-data" / "oil"

BIG_RECORD = json.load(open(TEST_DATA_DIR / "EC" / "EC02234.json", encoding="utf-8"))


@pytest.fixture
def big_record():
    return Oil.from_py_json(BIG_RECORD)


@pytest.fixture
def no_type_oil():
    no_type_oil = {'oil_id': 'AD00123', 'metadata': {'name': 'An oil name'}}
    return Oil.from_py_json(no_type_oil)


@pytest.fixture
def minimal_oil():
    oil = Oil('XXXXX')
    oil.metadata.name = "Minimal Oil for Tests"
    fresh = Sample()
    # print(fresh.physical_properties)
    oil.sub_samples.append(fresh)
    return oil


def test_validation_doesnt_change_oil(big_record):
    orig = copy.deepcopy(big_record)

    msgs = orig.validate()
    # gnome_suitable may have been reset
    big_record.metadata.gnome_suitable = orig.metadata.gnome_suitable
    assert orig == big_record


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
    except ValueError as err:
        print(str(err))
        assert ("E010: Record has no oil_id: every record must have an ID" in str(err))


@pytest.mark.parametrize("name", [
    "  ",
    "X",
    "4",
])
def test_reasonable_name(name):
    # unreasonable names should fail
    oil = Oil(oil_id='AD00123')
    oil.metadata.name = name
    validate(oil)

    assert snippet_in_oil_status("W001:", oil)


def test_no_type(no_type_oil):

    # print("oil.metadata")

    # print(no_type_oil.metadata)
    validate(no_type_oil)

    # print("status after validating")
    # for s in no_type_oil.status:
    #     print(s)
    assert snippet_in_oil_status("W002:", no_type_oil)


def test_bad_type(no_type_oil):
    no_type_oil.metadata.product_type = "Fred"
    validate(no_type_oil)

    for s in no_type_oil.status:
        print(s)
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
    oil.metadata.product_type = "Crude Oil NOS"
    validate(oil)
    assert snippet_in_oil_status("E030:", oil)


def test_no_api_not_crude(no_type_oil):
    oil = no_type_oil
    oil.metadata.product_type = "Solvent"
    validate(oil)
    assert snippet_in_oil_status("W004:", oil)


def test_api_outragious(no_type_oil):
    oil = no_type_oil
    oil.metadata.API = -200
    validate(oil)
    assert snippet_in_oil_status("W005:", oil)


def test_API_density_match(minimal_oil):
    oil = minimal_oil
    minimal_oil.metadata.API = 32.0
    density = DensityPoint(
        density=Density(value=0.86469, unit='g/cm^3'),
        ref_temp=Temperature(value=60, unit='F'),
    )
    oil.sub_samples[0].physical_properties.densities.append(density)

    density_at_60F = physical_properties.Density(oil).at_temp(60, 'F')
    API = uc.convert('kg/m^3', 'API', density_at_60F)
    print(density_at_60F)
    print(API)

    assert math.isclose(API, oil.metadata.API, rel_tol=1e3)

    msgs = oil.validate()

    print(msgs)
    assert False


def test_no_subsamples(no_type_oil):
    oil = no_type_oil
    validate(oil)
    assert snippet_in_oil_status("E031", oil)


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


def test_no_densities_with_density(big_record):
    oil = big_record
    validate(oil)

    assert snippet_not_in_oil_status("W006:", oil)


def test_no_densities(big_record):
    oil = big_record
    #print(oil.sub_samples[0])

    pp = oil.sub_samples[0].physical_properties
    del pp.densities[:]
    validate(oil)

    print(oil.status)

    assert snippet_in_oil_status("W006: No density values provided", oil)


def test_bad_value_in_dist_temp(big_record):
    oil = big_record
    oil.sub_samples[0].distillation_data.cuts[0].vapor_temp.value = -1000
    validate(oil)
    print(oil.status)

    assert snippet_in_oil_status("E040: Value for distillation vapor temp", oil)


# No longer checking for distillation cuts.
# def test_distillation_cuts(big_record):
#     oil = big_record

#     validate(oil)

#     assert snippet_not_in_oil_status("W007:", oil)

# def test_no_distillation_cuts(big_record):
#     oil = big_record

#     # remove the cut data
#     oil.sub_samples[0].distillation_data = []
#     validate(oil)
#     print(oil.status)

#     assert snippet_in_oil_status("W007:", oil)


def test_none_year_in_reference(big_record):
    oil = big_record

    oil.metadata.reference.year = None

    validate(oil)

    assert snippet_in_oil_status("W008", oil)


def test_bad_year_in_reference(big_record):
    oil = big_record

    oil.metadata.reference.year = -2000

    validate(oil)

    assert snippet_in_oil_status("E012", oil)


def test_good_year_in_reference(big_record):
    oil = big_record

    oil.metadata.reference.year = 2020

    validate(oil)

    assert snippet_not_in_oil_status("W1111", oil)
    assert snippet_not_in_oil_status("E1111", oil)


def test_does_not_break_test_records():
    """
    run validation on all the test data, just to make sure that
    nothing breaks
    """
    for rec, path in get_all_records(TEST_DATA_DIR):
        msgs = rec.validate()

    assert True
