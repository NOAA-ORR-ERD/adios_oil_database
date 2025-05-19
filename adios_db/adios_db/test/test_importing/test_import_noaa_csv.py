"""
Tests the importing from a "NOAA Standard" CSV file script.

Note: tests aren't comprehensive, but at least there's something.

If it breaks on future files - please add a test!

NOTE: you can see all the logging messages when running the tests by:

   pytest --log-cli-level debug

"""
from pathlib import Path

import pytest

from adios_db.util import BufferedIterator
from adios_db.computation.physical_properties import get_distillation_cuts
from adios_db.models.common.measurement import (MassFraction,
                                                Temperature,
                                                MassOrVolumeFraction,
                                                AnyUnit)
from adios_db.models.oil.oil import ADIOS_DATA_MODEL_VERSION
from adios_db.models.oil.physical_properties import (Density,
                                                     DensityPoint,
                                                     DynamicViscosity,
                                                     DynamicViscosityPoint,
                                                     PourPoint,
                                                     FlashPoint)

from adios_db.models.oil.sara import Sara
from adios_db.models.oil.compound import Compound
from adios_db.models.oil.bulk_composition import BulkComposition
from adios_db.models.oil.industry_property import IndustryProperty

from adios_db.data_sources.noaa_csv.reader import (read_csv,
                                                   read_measurement,
                                                   float_or_placeholder,
                                                   padded_csv_reader,
                                                   empty_measurement,
                                                   read_emulsions,
                                                   )

from adios_db.computation.gnome_oil import make_gnome_oil


# uncomment if you want to see all the debugging output on failure.
# adios_db.initialize_console_log(level='debug')


HERE = Path(__file__).parent
DATA_DIR = HERE / "example_data"
OUTPUT_DIR = HERE / "output_dir"
test_file1 = Path("LSU_AlaskaNorthSlope.csv")
test_file2 = Path("example_noaa_csv.csv")
test_file3 = Path("Average-VLSFO-AMSA-2022.csv")
test_file4 = Path("generic_d.csv")
test_file5 = Path("example_noaa_csv_with_emulsion.csv")


# make module level?
@pytest.fixture
def test_record():
    """
    read the example record and return the resulting oil record
    """
    return read_csv(DATA_DIR / test_file1)


@pytest.fixture
def csv_to_test_padding():
    fname = DATA_DIR / "csv_for_testing_padding.csv"

    with open(fname, 'w', encoding='utf-8') as outfile:
        outfile.write("this, that, the,,,\n"
                      "1,,3\n"
                      "3\n"
                      "6,,,,,,,,,\n"
                      )

    yield fname
    fname.unlink()


def test_padded_csv_reader(csv_to_test_padding):
    # padding with 20 to make sure
    reader = padded_csv_reader(csv_to_test_padding, 6)
    expected = (['this', ' that', ' the', '', '', ''],
                ['1', '', '3', '', '', ''],
                ['3', '', '', '', '', ''],
                ['6', '', '', '', '', '', '', '', '', ''],
                )
    for row, exrow in zip(reader, expected):
        assert len(row) >= 6
        assert row == exrow


def test_buffered_csv_reader(csv_to_test_padding):
    """
    we need to put rows back on the stack after reading them
    """
    reader = BufferedIterator(padded_csv_reader(csv_to_test_padding, 6))

    row = next(reader)
    assert row == ['this', ' that', ' the', '', '', '']

    row = next(reader)
    assert row == ['1', '', '3', '', '', '']
    reader.push(row)
    row = next(reader)
    assert row == ['1', '', '3', '', '', '']

    row = next(reader)
    assert row == ['3', '', '', '', '', '']

    row = next(reader)
    assert row == ['6', '', '', '', '', '', '', '', '', '']
    reader.push(row)
    row = next(reader)
    assert row == ['6', '', '', '', '', '', '', '', '', '']


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


@pytest.mark.parametrize('vals', [
    {'value': 0.0, 'min_value': None, 'max_value': None, 'unit': 'C'},
    {'value': None, 'min_value': 1.0, 'max_value': None, 'unit': 'C'},
    {'value': None, 'min_value': '', 'max_value': 2.0, 'unit': 'C'},
])
def test_empty_measurement_not_empty(vals):
    m = Temperature(**vals)
    assert not empty_measurement(m)


def test_empty_measurement():
    vals = {'value': None, 'min_value': None, 'max_value': None, 'unit': 'C'}
    m = Temperature(**vals)
    assert empty_measurement(m)


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


@pytest.mark.parametrize("attr, value", [
    ('pour_point', PourPoint(Temperature(32, unit='C'))),
    ('flash_point', FlashPoint(Temperature(max_value=-8, unit='C'))),
])
def test_subsample_physical_properties(attr, value, test_record):
    print(len(test_record.sub_samples))
    assert len(test_record.sub_samples) == 2
    pp = test_record.sub_samples[0].physical_properties
    print(attr, getattr(pp, attr))
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
    assert densities[0] == DensityPoint(
        density=Density(value=0.9123, unit='g/cm³', unit_type='density'),
        ref_temp=Temperature(value=32.0, unit='F', unit_type='temperature')
    )
    assert densities[1] == DensityPoint(
        density=Density(value=0.8663, unit='g/cm³', unit_type='density'),
        ref_temp=Temperature(value=15.0, unit='C', unit_type='temperature')
    )


def test_read_kvis(test_record):
    """
    test the code that reads the kinematic viscosity

    NOTE: test_record has none

    tested within the whole  reader, so that it will stay in sync
    with any changes
    """
    kvis = test_record.sub_samples[0].physical_properties.kinematic_viscosities

    assert len(kvis) == 0


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
    assert dvis[0] == DynamicViscosityPoint(
        viscosity=DynamicViscosity(value=23.2, unit='cP',
                                   unit_type='dynamicviscosity'),
        ref_temp=Temperature(value=0.0, unit='C', unit_type='temperature')
    )
    assert dvis[1] == DynamicViscosityPoint(
        viscosity=DynamicViscosity(value=11.5, unit='cP',
                                   unit_type='dynamicviscosity'),
        ref_temp=Temperature(value=15.0, unit='C', unit_type='temperature')
    )


def test_distillation_header():
    """
    make sure the distillation cuts are read correctly

    In the context of a real file
    """
    oil = read_csv(DATA_DIR / test_file3)

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
    oil = read_csv(DATA_DIR / test_file3)

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
    oil = read_csv(DATA_DIR / test_file3)

    sara = oil.sub_samples[0].SARA
    print(sara)

    assert sara == Sara(saturates=MassFraction(value=54.5, unit='%'),
                        aromatics=MassFraction(value=23.1, unit='%'),
                        resins=MassFraction(value=16.7, unit='%'),
                        asphaltenes=MassFraction(value=5.7, unit='%'))


def test_compounds():
    """
    The "example_noaa_csv.csv" has two compound:
    """
    oil = read_csv(DATA_DIR / test_file2)

    compounds = oil.sub_samples[0].compounds

    assert len(compounds) == 2
    assert compounds[0] == Compound(
        name='Biphenyl (Bph)',
        groups=[],
        method="",
        measurement=MassFraction(value=120.2, unit='µg/g')
    )
    assert compounds[1] == Compound(
        name='Pyrene (Py)',
        groups=['Other Priority PAHs'],
        method="ESTS 5.03/x.x/M",
        comment='Just an example',
        measurement=MassFraction(value=28.6, unit='µg/g')
    )


def test_bulk_composition():
    """
    The "example_noaa_csv.csv" has one bulk composition
    """
    oil = read_csv(DATA_DIR / test_file2)

    bulk_comp = oil.sub_samples[0].bulk_composition

    assert len(bulk_comp) == 1
    assert bulk_comp[0] == BulkComposition(
        name='Sulfur',
        measurement=MassOrVolumeFraction(value=0.0207,
                                         unit="%", unit_type="Mass Fraction")
    )


def test_industry_properties():
    """
    The "example_noaa_csv.csv" has one bulk composition
    """
    oil = read_csv(DATA_DIR / test_file2)

    ind_prop = oil.sub_samples[0].industry_properties

    assert len(ind_prop) == 1

    expected = IndustryProperty(
        name='Reid Vapor Pressure',
        method='a method',
        measurement=AnyUnit(value=0.7, unit="PSI", unit_type="pressure")
    )

    assert ind_prop[0] == expected


def test_multiple_subsamples():
    """
    not well tested, but some of the records from the CAFE project
    have something
    """
    oil = read_csv(DATA_DIR / test_file1)
    ss = oil.sub_samples[1]
    assert len(oil.sub_samples) == 2

    md = ss.metadata
    assert md.name == "30.5% Evaporated (lab weathered)"

    densities = ss.physical_properties.densities
    assert densities[0].density.value == 0.934
    assert densities[0].density.unit == 'g/cm³'

    dynamic_viscosities = ss.physical_properties.dynamic_viscosities
    assert dynamic_viscosities[0].viscosity.value == 4230
    assert dynamic_viscosities[0].viscosity.unit == 'cP'

    assert dynamic_viscosities[1].viscosity.value == 625
    assert dynamic_viscosities[1].viscosity.unit == 'cP'

    sulfur = BulkComposition(
        name='Sulfur Content',
        measurement=MassOrVolumeFraction(value=1.5, unit="%",
                                         unit_type="Mass Fraction")
    )

    assert ss.bulk_composition[0] == sulfur


def test_generic_csv():
    """
    tests reading the CSV file generated by the generic oils project
    """
    oil = read_csv(DATA_DIR / test_file4)

    md = oil.metadata
    oil.to_file(OUTPUT_DIR / test_file4.with_suffix(".json"))

    print(md)

    assert md.source_id[:5] == '2023-'
    assert md.reference.year == 2023
    assert md.reference.reference == "NOAA Technical Report on Generic Oils"
    assert md.product_type == 'Distillate Fuel Oil'

    assert len(oil.sub_samples) == 1

    ss = oil.sub_samples[0]

    assert ss.metadata.name == "Fresh Oil"
    pp = ss.physical_properties

    assert len(pp.densities) == 3
    assert len(pp.kinematic_viscosities) == 3

    dist = ss.distillation_data

    assert len(dist.cuts) == 21

    assert md.API == 34.28

    msgs = oil.validate()

    assert len(msgs) == 0

    # make sure it's GNOME Suitable
    go = make_gnome_oil(oil)


def test_read_emulsions():

    reader = BufferedIterator(padded_csv_reader(DATA_DIR / "Emulsion_example.csv"))
    # pop off the 'Emulsion Properties' line
    next(reader)
    el = read_emulsions(reader)

    assert len(el) == 2

    # only testing a few, but it's something
    emulsion = el[0]
    assert emulsion.age.value == 1
    assert emulsion.age.unit == 'day'
    assert emulsion.storage_modulus.value == 12.0

    # viscosity data
    assert len(emulsion.kinematic_viscosities) == 2
    assert len(emulsion.dynamic_viscosities) == 2

    emulsion = el[1]
    assert emulsion.age.value == 17
    assert emulsion.age.unit == 'day'
    assert emulsion.complex_modulus.value == 123.0
    # viscosity data
    assert len(emulsion.kinematic_viscosities) == 2
    assert len(emulsion.dynamic_viscosities) == 2


def test_emulsion_in_record():
    """
    check that emulsions are read properly

    NOTE: This is (so far) only testing a psuedo-emulsion record
          generated from "bullwinkle"
    """
    oil = read_csv(DATA_DIR / test_file5)

    assert len(oil.sub_samples) == 2

    # Emulsion data in the first subsample
    ss0 = oil.sub_samples[0]
    emulsions = ss0.environmental_behavior.emulsions
    assert len(emulsions) == 1
    emulsion = emulsions[0]
    assert emulsion.visual_stability == "Did not form"
    assert emulsion.ref_temp.value == 15
    assert emulsion.ref_temp.unit == "C"
    assert emulsion.water_content is None



    # Emulsion data in the second subsample
    ss0 = oil.sub_samples[1]
    emulsions = ss0.environmental_behavior.emulsions
    assert len(emulsions) == 1
    emulsion = emulsions[0]
    assert emulsion.visual_stability == "Unknown stability"
    assert emulsion.ref_temp.value == 15
    assert emulsion.ref_temp.unit == "C"
    assert emulsion.water_content.value == 0.7
    assert emulsion.water_content.unit == "fraction"

@pytest.mark.parametrize('filename', [
    test_file1,
    test_file2,
    test_file3,
    test_file4,  # need valid generic diesel record first
    test_file5,  # should check bullwinkle at some point
])
def test_full_record(filename):
    """
    tests a modestly complete record
    """
    oil = read_csv(DATA_DIR / filename)
    outfilename = OUTPUT_DIR / filename.with_suffix(".json")
    print("writing:", outfilename)

    oil.to_file(outfilename)

    msgs = oil.validate()
    assert len(msgs) == 0

    # make sure it's GNOME Suitable
    go = make_gnome_oil(oil)




