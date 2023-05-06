"""
Tests the importing from a "NOAA Standard" CSV file script.

Note: tests aren't comprehensive, but at least there's something.

If it breaks on future files - please add a test!
"""
from pathlib import Path

import pytest

from adios_db.computation.physical_properties import get_distillation_cuts
from adios_db.models.common.measurement import MassFraction, Temperature, MassOrVolumeFraction, AnyUnit
from adios_db.models.oil.oil import ADIOS_DATA_MODEL_VERSION
from adios_db.models.oil.physical_properties import (Density,
                                                     DensityPoint,
                                                     DynamicViscosity,
                                                     DynamicViscosityPoint
                                                     )

from adios_db.models.oil.sara import Sara
from adios_db.models.oil.compound import Compound
from adios_db.models.oil.bulk_composition import BulkComposition
from adios_db.models.oil.industry_property import IndustryProperty

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
                                               ("  fraction ", None),
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

def test_distillation_header():
    """
    make sure the distillation cuts are read correctly

    In the context of a real file
    """
    oil = read_csv(test_file3)

    dist = oil.sub_samples[0].distillation_data

    assert dist.type.lower() == "mass fraction"
    assert dist.method == ""
    assert dist.end_point is None
    assert dist.fraction_recovered.value == 100
    assert dist.fraction_recovered.unit == '%'


def test_distillation_cuts():
    """
    make sure the distillation cuts are read correctly

    In the context of a real file
    """
    oil = read_csv(test_file3)

    # cuts = oil.sub_samples[0].distillation_data.cuts

    # to make it easier to read and test
    cuts = get_distillation_cuts(oil, temp_units='C')

    print(cuts)

    assert cuts == [(0.015, 196.0),
                    (0.051, 216.0),
                    (0.095, 236.0),
                    (0.14, 263.0),
                    (0.223, 287.0),
                    (0.265, 302.0),
                    (0.347, 331.0),
                    (0.423, 357.0),
                    (0.492, 380.0),
                    (0.555, 402.0),
                    (0.631, 432.0),
                    (0.708, 459.0),
                    (0.777, 483.0),
                    (0.822, 498.0),
                    (0.873, 512.0)]

def test_sara():
    """
    make sure the sara are read correctly

    In the context of a real file
    """
    oil = read_csv(test_file3)

    sara = oil.sub_samples[0].SARA

    print(sara)
    assert sara == Sara(saturates={'value': 54.5, 'unit': '%'},
                        aromatics={'value': 23.1, 'unit': '%'},
                        resins={'value': 16.7, 'unit': '%'},
                        asphaltenes={'value': 5.7, 'unit': '%'})


def test_compounds():
    """
    The "example_noaa_csv.csv" has two compound:
    """
    oil = read_csv(test_file2)

    compounds = oil.sub_samples[0].compounds

    assert len(compounds) == 2
    assert compounds[0] == Compound(name='Biphenyl (Bph)',
                                    groups=[],
                                    method="",
                                    measurement=MassFraction(value=120.2,
                                                             unit='µg/g',
                                                             ))
    assert compounds[1] == Compound(name='Pyrene (Py)',
                                    groups=['Other Priority PAHs'],
                                    method="ESTS 5.03/x.x/M",
                                    comment='Just an example',
                                    measurement=MassFraction(value=28.6,
                                                             unit='µg/g',
                                                             ))

def test_bulk_composition():
    """
    The "example_noaa_csv.csv" has one bulk composition
    """
    oil = read_csv(test_file2)

    bulk_comp = oil.sub_samples[0].bulk_composition

    assert len(bulk_comp) == 1
    assert bulk_comp[0] == BulkComposition(name='Sulfur',
                                           measurement=MassOrVolumeFraction(value=0.0207,
                                                                            unit="%",
                                                                            unit_type="Mass Fraction"))
def test_industry_properties():
    """
    The "example_noaa_csv.csv" has one bulk composition
    """
    oil = read_csv(test_file2)

    ind_prop = oil.sub_samples[0].industry_properties

    assert len(ind_prop) == 1

    expected = IndustryProperty(name='Reid Vapor Pressure',
                               method='a method',
                               measurement=AnyUnit(value=0.7,
                                                   unit="PSI",
                                                   unit_type="pressure"))

    assert ind_prop[0] == expected

def test_full_record():
    """
    tests a modestly complete record
    """

    oil = read_csv(test_file3)

    msgs = oil.validate()
    assert not msgs

    oil.to_file(HERE / "example_data" / "Average-VLSFO-AMSA-2022.json")





