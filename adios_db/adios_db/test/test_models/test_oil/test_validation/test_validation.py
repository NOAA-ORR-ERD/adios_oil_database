"""
tests of the validation code

most need to be updated to test validating an Oil object directly
"""
from pathlib import Path
import math
import copy
import json

import pytest

import nucos

from adios_db.computation import physical_properties
from adios_db.models.common.measurement import Density, Temperature
from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.distillation import Distillation
from adios_db.models.oil.physical_properties import DensityPoint
from adios_db.models.oil.validation.validate import validate_json, validate
from adios_db.models.oil.validation import (unpack_status,
                                            is_only_ignored,
                                            ERRORS_TO_IGNORE,
                                            is_not_iso_or_year,
                                            )

from adios_db.scripting import get_all_records


HERE = Path(__file__).parent

TEST_DATA_DIR = (HERE.parent.parent.parent /
                 "data_for_testing" / "noaa-oil-data" / "oil")
BIG_RECORD = json.load(open(TEST_DATA_DIR / "EC" / "EC02234.json",
                            encoding="utf-8"))


# tests for the validation utilities
def test_unpack_status():
    status = ["W005: API value: 2256.95 seems unlikely",
              "W009: Distillation fraction recovered is missing or invalid",
              "W009: Another one with the same Code"]
    result = unpack_status(status)

    print(result)

    assert result.keys() == {"W005", "W009"}
    assert len(result["W005"]) == 1
    assert len(result["W009"]) == 2
    assert "Another one with the same Code" in result["W009"]


def test_is_only_ignored_true():
    status_dict = {code: ["random message text"] for code in ERRORS_TO_IGNORE}

    assert is_only_ignored(status_dict)


def test_is_only_ignored_false():
    status_dict = {code: ["random message text"] for code in ERRORS_TO_IGNORE}
    # add one we know won't ever be in the ignore list
    status_dict["F32"] = ["nothing important"]

    assert not is_only_ignored(status_dict)


def test_is_not_iso_or_year_good():
    assert is_not_iso_or_year("2021-12-03") is False


def test_is_not_iso_or_year_bad():
    assert is_not_iso_or_year("2x021-12-03") == 'must be a year or iso datestring'


def test_is_not_iso_or_year_year():
    assert is_not_iso_or_year("2021") is False


def test_is_not_iso_or_year_bad_year():
    assert is_not_iso_or_year("123") == 'must be a valid year or iso datestring'



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
    oil.sub_samples.append(fresh)

    return oil


def test_validation_doesnt_change_oil(big_record):
    orig = copy.deepcopy(big_record)
    orig.validate()

    # gnome_suitable may have been reset
    big_record.metadata.gnome_suitable = orig.metadata.gnome_suitable
    assert orig == big_record


def snippet_in_oil_status(snippet, msgs):
    """
    checks if the particular snippet in one of the messages
    """
    try:
        msgs = msgs.status
    except AttributeError:
        # must not be an oil object -- assume it's a list of messages
        pass

    for msg in msgs:
        if snippet in msg:
            return True

    return False


def snippet_not_in_oil_status(snippet, oil):
    """
    checks if the particular snippet in one of the messages
    """
    return not snippet_in_oil_status(snippet, oil)


class TestFromPyJson:
    def test_sample_metadata(self):
        oil = Oil.from_py_json({
            'oil_id': "XX123456",
            'metadata': {
                'name': "An oil name"
            },
            'sub_samples': [
                {
                    'metadata': {
                        'fraction_evaporated': {'value': 11, 'unit': '%',
                                                'unit_type': 'massfraction'}
                    }
                 }
            ]
        })

        print(oil.sub_samples[0].metadata)
        print(oil.sub_samples[0].metadata.fraction_evaporated)

        assert len(oil.sub_samples) > 0
        assert oil.sub_samples[0].metadata.name == 'Fresh Oil Sample'
        assert oil.sub_samples[0].metadata.short_name == 'Fresh Oil'
        assert oil.sub_samples[0].metadata.fraction_evaporated is not None


class TestValidateJson:
    def test_no_id(self):
        """
        should get a particular ValueError if you try an invalid dict
        """
        try:
            validate_json({"this": 3})
        except ValueError as err:
            print(str(err))
            assert ("E010: Record has no oil_id: every record must have an ID"
                    in str(err))

    def test_sample_metadata(self):
        oil = validate_json({
            'oil_id': "XX123456",
            'metadata': {
                'name': "An oil name"
            },
            'sub_samples': [
                {
                    'metadata': {
                        'fraction_evaporated': {'value': 11, 'unit': '%',
                                                'unit_type': 'massfraction'}
                    }
                }
            ]
        })

        print(oil.sub_samples[0].metadata)
        print(oil.sub_samples[0].metadata.fraction_evaporated)

        assert len(oil.sub_samples) > 0
        assert oil.sub_samples[0].metadata.name == 'Fresh Oil Sample'
        assert oil.sub_samples[0].metadata.short_name == 'Fresh Oil'
        assert oil.sub_samples[0].metadata.fraction_evaporated is not None


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
    validate(no_type_oil)

    assert snippet_in_oil_status("W002:", no_type_oil)


def test_bad_type(no_type_oil):
    no_type_oil.metadata.product_type = "Fred"
    validate(no_type_oil)

    assert snippet_in_oil_status("W003:", no_type_oil)


def test_correct_type(no_type_oil):
    no_type_oil.metadata.product_type = "Crude"
    validate(no_type_oil)

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

    assert snippet_in_oil_status("W002", oil)


def test_no_api_crude(no_type_oil):
    oil = no_type_oil
    oil.metadata.product_type = "Crude Oil NOS"

    validate(oil)

    assert snippet_in_oil_status("E030:", oil)


def test_no_api_not_crude(no_type_oil):
    # we've turned off these warnings
    oil = no_type_oil
    oil.metadata.product_type = "Solvent"

    validate(oil)

    assert snippet_not_in_oil_status("W004:", oil)


def test_api_outragious(no_type_oil):
    oil = no_type_oil
    oil.metadata.API = -200

    validate(oil)

    assert snippet_in_oil_status("W005:", oil)


def test_API_density_match(minimal_oil):
    oil = minimal_oil
    minimal_oil.metadata.API = 32.1  # close enough to 32.0

    density = DensityPoint(
        density=Density(value=0.86469, unit='g/cm^3'),
        ref_temp=Temperature(value=60, unit='F'),
    )
    oil.sub_samples[0].physical_properties.densities.append(density)

    density_at_60F = physical_properties.Density(oil).at_temp(60, 'F')
    API = nucos.convert('kg/m^3', 'API', density_at_60F)

    assert math.isclose(API, oil.metadata.API, rel_tol=1e3)

    validate(oil)

    assert snippet_not_in_oil_status("E043", oil)


def test_API_density_missmatch(minimal_oil):
    oil = minimal_oil
    minimal_oil.metadata.API = 32.2  # too far from 32.0

    density = DensityPoint(  # API 32.0 converted
        density=Density(value=0.86469, unit='g/cm^3'),
        ref_temp=Temperature(value=60, unit='F'),
    )
    oil.sub_samples[0].physical_properties.densities.append(density)

    density_at_60F = physical_properties.Density(oil).at_temp(60, 'F')
    print(f"{density_at_60F=}")

    API = nucos.convert('kg/m^3', 'API', density_at_60F)
    print(f"{API=}")
    print(f"{minimal_oil.metadata.API=}")

    validate(oil)

    print(oil.status)

    assert snippet_in_oil_status("E043", oil)


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

    pp = oil.sub_samples[0].physical_properties
    del pp.densities[:]

    validate(oil)

    assert snippet_in_oil_status("W006: No density values provided", oil)


def test_bad_value_in_dist_temp(big_record):
    oil = big_record
    oil.sub_samples[0].distillation_data.cuts[0].vapor_temp.value = -1000

    validate(oil)

    assert snippet_in_oil_status("E040: Value for distillation vapor temp",
                                 oil)


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
    for rec, _path in get_all_records(TEST_DATA_DIR):
        print("Validating:", _path)
        _msgs = rec.validate()

    assert True


@pytest.mark.skipif(not hasattr(nucos, 'is_supported_unit'),
                    reason='nucos too old for unit checking')
def test_bad_unit():
    """
    Making sure a bad unit trickles up through the validation
    """
    record_file = (HERE.parent.parent.parent
                   / "data_for_testing" / "example_data"
                   / "RecordWithUnitErrors.json")

    oil = Oil.from_file(record_file)
    msgs = oil.validate()

    expected_errors = [
        "E045: Unit: 'g/oz' is not a valid unit for unit type: 'density'",
        "E045: Unit: 'Celcius' is not a valid unit for unit type: "
        "'temperature'",
    ]

    for err in expected_errors:
        for msg in msgs:
            if err in msg:
                break
        else:
            assert False, f'"{err}" not in validation messages'


def test_gnome_suitable_true():
    """
    running an gnome suitable oil should set the flag to True
    """
    oil = Oil.from_file(TEST_DATA_DIR / "EC" / "EC00506.json")

    print(oil.metadata.gnome_suitable)
    msgs = oil.validate()
    assert oil.metadata.gnome_suitable
    # NOTE: these might change if data are fixed
    # missing interfacial tension and distillation duplicates
    for msg in msgs:
        print(msg)
    num_expected = 2
    for msg in msgs:
        if msg.startswith("E044:"):
            num_expected += 1
        if msg.startswith("W012:"):  # location in wrong order
            num_expected += 1
    assert num_expected == len(msgs)


def test_gnome_suitable_false():
    """
    running an not gnome suitable oil should set the flag to False
    and add a message to the Warnings.
    """
    oil = Oil.from_file(TEST_DATA_DIR / "EC" / "EC02234.json")

    # remove dist data
    oil.sub_samples[0].distillation_data = Distillation()
    print(oil.metadata.gnome_suitable)
    msgs = oil.validate()
    print(oil.metadata.gnome_suitable)
    assert not oil.metadata.gnome_suitable
    print(msgs)
    # 2 missing interfacial tension and no distillation for GNOME
    num_expected = 3

    for msg in msgs:
        print(msg)
        if msg.startswith("E044:"):
            num_expected += 1
        if msg.startswith("W012:"): # Canada, Alberta in wrong order
            num_expected += 1
    assert num_expected == len(msgs)


