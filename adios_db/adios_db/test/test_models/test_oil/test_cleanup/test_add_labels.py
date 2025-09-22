"""
tests for adding suggested labels to oil
"""
from pathlib import Path
import pytest

from adios_db.models.common import measurement as meas
from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.physical_properties import KinematicViscosityPoint, DensityPoint
from adios_db.models.oil.cleanup.add_labels import get_suggested_labels, get_sulfur_labels

DATA_DIR = TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data_for_testing" / "example_data/"


def add_kin_viscosity_to_oil(oil,
                             viscosities,
                             temp,
                             unit,
                             kvis_temp=15.0,
                             temp_unit="C"):
    """
    utility for making test oils with given viscosities.
    """
    try:
        sample = oil.sub_samples[0]
    except IndexError:
        sample = Sample()
        sample.metadata.name = "only viscosity"
        oil.sub_samples.append(sample)
    for kvis in viscosities:
        kp = KinematicViscosityPoint(
            meas.KinematicViscosity(kvis, unit=unit),
            meas.Temperature(kvis_temp, unit=temp_unit))
        sample.physical_properties.kinematic_viscosities.append(kp)
    return None


def add_density_to_oil(oil,
                       densities,
                       temp,
                       unit,
                       dens_temp=15.0,
                       temp_unit="C"):
    """
    utility for making test oils with given densities.
    """
    try:
        sample = oil.sub_samples[0]
    except IndexError:
        sample = Sample()
        sample.metadata.name = "only density"
        oil.sub_samples.append(sample)
    for dens in densities:
        dp = DensityPoint(
            meas.Density(dens, unit="kg/m^3"),
            meas.Temperature(dens_temp, unit=temp_unit))
        sample.physical_properties.densities.append(dp)
    return None


def test_add_labels_to_oil_no_product_type():
    """
    this oil should get no labels
    """
    oil = Oil('XXXXX')

    assert get_suggested_labels(oil) == []


def test_add_labels_to_oil_no_API():
    """
    this oil should get only labels with no API limits
    """
    oil = Oil('XXXXX')
    oil.metadata.product_type = 'Crude Oil NOS'

    assert get_suggested_labels(oil) == ['Crude Oil']


def test_add_labels_to_oil_no_labels_other():
    """
    we should never get a label for 'Other'
    """
    oil = Oil('XXXXX')
    oil.metadata.API = 32.0
    oil.metadata.product_type = 'Other'

    assert get_suggested_labels(oil) == []


@pytest.mark.parametrize('pt, api, labels', [
    ('Crude Oil NOS', 35.0, {'Light Crude', 'Crude Oil'}),
    ('Crude Oil NOS', 25.0, {'Medium Crude', 'Crude Oil'}),
    ('Crude Oil NOS', 19.0, {'Heavy Crude', 'Crude Oil'}),
    ('Crude Oil NOS', 9.9, {'Heavy Crude', 'Group V', 'Crude Oil'}),
    ('Tight Oil', 32, {'Tight Oil', 'Fracking Oil', 'Shale Oil', 'Crude Oil'}),
    ('Residual Fuel Oil', 13, {'No. 6 Fuel Oil', 'Refined Product', 'Bunker C',
                               'Residual Fuel', 'Fuel Oil', 'HFO',
                               'Heavy Fuel Oil'}),
    ('Residual Fuel Oil', 16, {'Fuel Oil', 'IFO', 'Refined Product',
                               'Residual Fuel'}),
    ('Distillate Fuel Oil', 32, {'Diesel', 'Distillate Fuel', 'Fuel Oil',
                                 'Home Heating Oil', 'MDO', 'No. 2 Fuel Oil',
                                 'Refined Product', 'Gas Oil'}),
])
def test_add_labels_to_oil_api(pt, api, labels):
    """
    we should never get a label for 'Other'
    """
    oil = Oil('XXXXX')
    oil.metadata.API = api
    oil.metadata.product_type = pt

    assert get_suggested_labels(oil) == sorted(labels)


@pytest.mark.parametrize('pt, api, kvis, kvis_temp, labels', [
    ('Distillate Fuel Oil', 32.0, 3, 38, {
        'Distillate Fuel', 'Refined Product', 'Fuel Oil', 'No. 2 Fuel Oil',
        'Gas Oil', 'Diesel', 'Home Heating Oil', 'MDO'
    }),
    ('Distillate Fuel Oil', 32.0, 6, 38, {
        'Distillate Fuel', 'Refined Product', 'Fuel Oil', 'MDO'
    }),
    ('Distillate Fuel Oil', 32.0, 1, 38, {
        'Distillate Fuel', 'Refined Product', 'Fuel Oil', 'MDO'
    }),
    # HFOs
    ('Residual Fuel Oil', 13.0, 390, 50, {
        'No. 6 Fuel Oil', 'Refined Product', 'Bunker C', 'Residual Fuel',
        'Fuel Oil', 'Heavy Fuel Oil', 'HFO'
    }),
    # IFOs
    ('Residual Fuel Oil', 29.0, 12, 38, { # ends up as kvis slightley higher than 4 at 50C
        'Refined Product', 'Residual Fuel', 'Fuel Oil', 'IFO'
    }),
])
def test_add_labels_to_oil_api_and_visc(pt, api, kvis, kvis_temp, labels):
    """
    refined products with density and viscosity limits
    """
    oil = Oil('XXXXX')
    oil.metadata.API = api
    oil.metadata.product_type = pt
    dens = 870 # single viscosity data sets require density for kv_2 calculation
    add_kin_viscosity_to_oil(oil, (kvis, ), 15, 'cSt', kvis_temp, 'C')
    add_density_to_oil(oil, (dens, ), 15, 'kg/m^3', kvis_temp, 'C')

    assert get_suggested_labels(oil) == sorted(labels)


def test_get_sulfur_labels_ulfo():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    labels = get_sulfur_labels(oil)

    assert labels == {'LSFO', 'ULSFO', 'VLSFO'}


def test_get_sulfur_labels_vlfo():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    labels = get_sulfur_labels(oil)

    assert labels == {'LSFO', 'ULSFO', 'VLSFO'}


def test_get_sulfur_labels_vlfo():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    for compound in oil.sub_samples[0].bulk_composition:
        if 'sulfur' in compound.name.lower():
            sulfur = compound.measurement.value = 0.4
    labels = get_sulfur_labels(oil)


    assert labels == {'LSFO', 'VLSFO'}


def test_get_sulfur_labels_lfo():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    for compound in oil.sub_samples[0].bulk_composition:
        if 'sulfur' in compound.name.lower():
            sulfur = compound.measurement.value = 0.6
    labels = get_sulfur_labels(oil)


    assert labels == {'LSFO'}


def test_get_sulfur_labels_not_low():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    for compound in oil.sub_samples[0].bulk_composition:
        if 'sulfur' in compound.name.lower():
            sulfur = compound.measurement.value = 2.0
    labels = get_sulfur_labels(oil)


    assert labels == set()


def test_get_sulfur_labels_not_data():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    for compound in oil.sub_samples[0].bulk_composition:
        if 'sulfur' in compound.name.lower():
            compound.name = "something else"
    labels = get_sulfur_labels(oil)

    assert labels == set()


def test_full_record_all_labels():
    oil = Oil.from_file(DATA_DIR / "SimpleULSFO.json")

    labels = get_suggested_labels(oil)

    assert set(labels) == set([
        'Diesel',
        'Distillate Fuel',
        'Fuel Oil',
        'Gas Oil',
        'Home Heating Oil',
        'MDO',
        'No. 2 Fuel Oil',
        'Refined Product',
        'ULSFO',
        'VLSFO',
        'LSFO',
    ])
