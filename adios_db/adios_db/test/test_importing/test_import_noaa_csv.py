"""
Tests the importing from a "NOAA Standard" CSV file script.

Note: tests aren't comprehensive, but at least there's something.

If it breaks on future files - please add a test!
"""
from pathlib import Path

import pytest

from adios_db.models.common.measurement import MassFraction, Temperature
from adios_db.models.oil.oil import ADIOS_DATA_MODEL_VERSION
from adios_db.models.oil.physical_properties import (Density,
                                                     DensityPoint,
                                                     DynamicViscosity,
                                                     DynamicViscosityPoint
                                                     )

from adios_db.data_sources.noaa_csv.reader import (read_csv,
                                                   read_measurement,
                                                   float_or_placeholder,
                                                   )


HERE = Path(__file__).parent

test_file1 = HERE / "example_data" / "LSU_AlaskaNorthSlope.csv"
test_file2 = HERE / "example_data" / "example_noaa_csv.csv"
test_file3 = HERE / "example_data" / "Average-VLSFO-AMSA-2022.csv"


# make module level?
@pytest.fixture
def test_record():
    """
    read the example record and return the resulting oil record
    """
    oil = read_csv(test_file1)

    return oil


def test_read_csv(test_record):
    """
    one big honking test for the whole thing -- not ideal, but something
    """
    oil = test_record

    assert oil.adios_data_model_version == ADIOS_DATA_MODEL_VERSION


@pytest.mark.parametrize(('val', 'expected'), [("3.3", 3.3),
                                               ("  3.3 ", 3.3),
                                               ("  3", 3.0),
                                               ("min_value", None),
                                               ("  ", None),
                                               ("", None),
                                               ])
def test_float_or_placeholder(val, expected):
    """
    make sure it returns None for empty and placeholder values
    """
    assert float_or_placeholder(val) == expected


def test_float_or_placeholder_bad():
    """
    make sure it returns None for empty and placeholder values
    """
    with pytest.raises(ValueError):
        float_or_placeholder("random non number")

    with pytest.raises(ValueError):
        float_or_placeholder("1.2.3")



def test_metadata(test_record):
    """
    Not really an isolated test, but at least errors will be a bit more
    specific
    """
    md = test_record.metadata
    test_map = [
        ("name", "Alaska North Slope"),
        ("source_id", ""),
        ("location", "Alaska, USA"),
        ("sample_date", "2009"),
        ("comments", ("The data in this record may have been compiled "
                      "from multiple sources and reflect samples of "
                      "varying age and composition")),
        ("product_type", "Crude Oil NOS"),
        ("API", 32.1),
    ]

    for attr, value in test_map:
        assert getattr(md, attr) == value

    assert md.reference.year == 2011
    assert md.reference.reference == (
        "Martin, J. (2011). Comparative toxicity and bioavailability "
        "of heavy fuel oils to fish using different exposure "
        "scenarios(Doctoral dissertation)."
    )
    assert set(md.alternate_names) == set(['ANS'])
    assert set(md.labels) == set(['Medium Crude', 'Crude Oil'])


@pytest.mark.parametrize("attr, value", [
    ("name", "Original fresh oil sample"),
    ("short_name", "Fresh"),
    ("sample_id", 'x1x1x1'),
    ("description", 'Just a little bit of text.'),
    ("fraction_evaporated", MassFraction(0.034, unit='fraction')),
    ("boiling_point_range", Temperature(min_value=150, max_value=250,
                                        unit='C')),
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

    assert vals == {'min_value': 1.2, 'value': None, 'max_value': None,
                    'unit': 'unit'}


def test_read_densities(test_record):
    """
    test the code that reads the density data

    tested within the whole  reader, so that it will stay in sync
    with any changes
    """
    densities = test_record.sub_samples[0].physical_properties.densities

    for dp in densities:
        print(dp)
    assert densities[0] == DensityPoint(density=Density(value=0.9123, unit='g/cm³', unit_type='density'),
                                        ref_temp=Temperature(value=32.0, unit='F', unit_type='temperature'))
    assert densities[1] == DensityPoint(density=Density(value=0.8663, unit='g/cm³', unit_type='density'),
                                        ref_temp=Temperature(value=15.0, unit='C', unit_type='temperature'))


def test_read_kvis(test_record):
    """
    test the code that reads the kinematic viscosity

    NOTE: test_record has none

    tested within the whole  reader, so that it will stay in sync
    with any changes
    """
    kvis = test_record.sub_samples[0].physical_properties.kinematic_viscosities

    assert len(kvis) == 0
    # for dp in densities:
    #     print(dp)
    # assert densities[0] == DensityPoint(density=Density(value=0.9123, unit='g/cm³', unit_type='density'),
    #                                     ref_temp=Temperature(value=32.0, unit='F', unit_type='temperature'))
    # assert densities[1] == DensityPoint(density=Density(value=0.8663, unit='g/cm³', unit_type='density'),
    #                                     ref_temp=Temperature(value=15.0, unit='C', unit_type='temperature'))

def test_read_dvis(test_record):
    """
    test the code that reads the kinematic viscosity

    NOTE: test_record has none

    tested within the whole  reader, so that it will stay in sync
    with any changes
    """
    dvis = test_record.sub_samples[0].physical_properties.dynamic_viscosities

    assert len(dvis) == 2
    for dvp in dvis:
        print(dvp)
    assert dvis[0] == DynamicViscosityPoint(viscosity=DynamicViscosity(value=23.2, unit='cP', unit_type='dynamicviscosity'),
                                            ref_temp=Temperature(value=0.0, unit='C', unit_type='temperature'))
    assert dvis[1] == DynamicViscosityPoint(viscosity=DynamicViscosity(value=11.5, unit='cP', unit_type='dynamicviscosity'),
                                            ref_temp=Temperature(value=15.0, unit='C', unit_type='temperature'))

def test_distillation():
    """
    make sure the distillation cuts are read correctly

    In the context of a real file
    """
    oil = read_csv(test_file3)

    dist = oil.sub_samples[0].distillation_data

    print(dist)

    assert False



# def test_load():
#     """
#     Just to have more than one -- very basic test

#     test whether the whole thing loads

#     This isn't really unit testing, but I'm lazy right now :-(
#     """
#     oil = read_csv(test_file2)

#     assert oil.metadata.name == "DMA, Chevron -- 2021"
#     assert oil.metadata.API == 36.5
#     assert oil.metadata.source_id == "xx-123"
#     assert oil.metadata.alternate_names == ["Fred", "Bob"]
#     assert oil.metadata.location == "California"

#     assert oil.metadata.reference.year == 2021
#     assert oil.metadata.reference.reference == 'Barker, C.H. 2021. "A CSV file reader for the ADIOS Oil Database."'
