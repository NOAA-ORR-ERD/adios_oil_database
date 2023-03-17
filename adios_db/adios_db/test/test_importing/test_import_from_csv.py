"""
Tests the importing from a "NOAA Standard" CSV file script.

Note: tests aren't comprehensive, but at least there's something.

If it breaks on future files - please add a test!
"""

from pathlib import Path

from adios_db.models.oil.oil import ADIOS_DATA_MODEL_VERSION
from adios_db.models.oil.metadata import MetaData
from adios_db.models.common.measurement import MassFraction, Temperature

from adios_db.scripts.import_csv import read_csv_file, read_measurement

import pytest

test_file = Path(__file__).parent / "example_data" / "LSU_AlaskaNorthSlope.csv"

# make module level?
@pytest.fixture
def test_record():
    """
    read the example record and return the resulting oil record
    """
    oil = read_csv_file(test_file)

    return oil

def test_read_csv(test_record):
    """
    one big honking test for the whole thing -- not ideal, but something
    """
    oil = test_record

    assert oil.adios_data_model_version == ADIOS_DATA_MODEL_VERSION


def test_metadata(test_record):
    """
    not really an isolated test, but at least errors will be a bit more specific
    """
    md = test_record.metadata
    test_map = [
        ("name", "Alaska North Slope"),
        ("source_id", ""),
        ("location", "Alaska, USA"),
        ("sample_date", "2009"),
        ("comments", "The data in this record may have been compiled from multiple sources and reflect samples of varying age and composition"),
        ("product_type", "Crude Oil NOS"),
        ("API", 32.1),
    ]

    for attr, value in test_map:
        assert getattr(md, attr) == value

    assert md.reference.year == 2011
    assert md.reference.reference == "Martin, J. (2011). Comparative toxicity and bioavailability of heavy fuel oils to fish using different exposure scenarios(Doctoral dissertation)."
    assert set(md.alternate_names) == set(['ANS'])
    assert set(md.labels) == set(['Medium Crude', 'Crude Oil'])

# def test_subsamples(test_record):
#     assert len(test_record.sub_samples) == 3

@pytest.mark.parametrize("attr, value",
                         [("name", "Original fresh oil sample"),
                          ("short_name", "Fresh"),
                          ("sample_id", 'x1x1x1'),
                          ("description", 'Just a little bit of text.'),
                          ("fraction_evaporated", MassFraction(0.034, unit='fraction')),
                          ("boiling_point_range", Temperature(min_value=150, max_value=250, unit='C')),
                          ])
def test_subsample_metadata_0(attr, value, test_record):
    md = test_record.sub_samples[0].metadata
    assert getattr(md, attr) == value

@pytest.mark.parametrize("attr, value",
                         [('pour_point', Temperature(32, unit='C')),
                          ('flash_point', Temperature(max_value=-8, unit='C')),
                          ])
def test_subsample_physical_properties(attr, value, test_record):
    pp = test_record.sub_samples[0].physical_properties
    assert getattr(pp, attr) == value

def test_read_measurement():
    vals = read_measurement(('1.2', '', ' ', 'unit '))

    assert vals == {'min_value': 1.2, 'value': None, 'max_value': None, 'unit': 'unit'}



