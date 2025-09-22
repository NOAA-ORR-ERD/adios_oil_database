"""
tests for making a GNOME Oil
"""
from pathlib import Path
from math import isclose

import pytest

from adios_db.models.oil.oil import Oil
from adios_db.computation.gnome_oil import (make_gnome_oil,
                                            sara_totals,
                                            estimate_pour_point)
from adios_db.computation.physical_properties import get_kinematic_viscosity_data


HERE = Path(__file__).parent
EXAMPLE_DATA_DIR = HERE.parent / "data_for_testing" / "example_data"
full_oil_filename = EXAMPLE_DATA_DIR / "ExampleFullRecord.json"
sparse_oil_filename = EXAMPLE_DATA_DIR / "ExampleSparseRecord.json"


# use the function if you're going to change the Oil object.
def get_full_oil():
    return Oil.from_file(full_oil_filename)


def get_sparse_oil():
    return Oil.from_file(sparse_oil_filename)


FullOil = get_full_oil()
SparseOil = get_sparse_oil()

# run it through the Oil object to make sure its up to date:
try:
    FullOil.to_file(full_oil_filename)
except Exception:  # in case the tests are running somewhere read-only
    pass


def test_metadata():
    """
    does it get the basic metadata right?
    """
    data = make_gnome_oil(FullOil)

    assert data['name'] == FullOil.metadata.name
    assert data['adios_oil_id'] == "EC02234"

    # The API might change
    # assert data['api'] == FullOil.metadata.API


def test_physical_properties():
    data = make_gnome_oil(FullOil)

    assert isclose(data['pour_point'], 248.15)


def test_densities():
    data = make_gnome_oil(FullOil)

    assert list(data['densities']) == [939.88, 925.26]
    assert list(data['density_ref_temps']) == [273.15, 288.15]
    assert list(data['density_weathering']) == [0.0, 0.0]


def test_kvis():
    data = make_gnome_oil(FullOil)

    assert list(data['kvis']) == [0.0013831552964208198, 0.0003782720532607051]
    assert list(data['kvis_ref_temps']) == [273.15, 288.15]
    assert list(data['kvis_weathering']) == [0.0, 0.0]


def test_kvis_single_value():
    test_oil = EXAMPLE_DATA_DIR / "SimpleULSFO.json"
    FullOil = Oil.from_file(test_oil)
    viscosities = get_kinematic_viscosity_data(FullOil, units="m^2/s",
                                               temp_units="K")

    assert len(viscosities) == 1	# original file has one viscosity
    data = make_gnome_oil(FullOil)
    assert len(data['kvis']) == 2	# gnome_oil has two viscosities


def test_bad_kvis_exception():
    test_oil = EXAMPLE_DATA_DIR / "AD00813.json"
    FullOil = Oil.from_file(test_oil)

    with pytest.raises(ValueError):
        data = make_gnome_oil(FullOil)

def test_no_kvis_exception():
    test_oil = EXAMPLE_DATA_DIR / "EC00622-no-visc.json"
    FullOil = Oil.from_file(test_oil)

    with pytest.raises(ValueError):
        data = make_gnome_oil(FullOil)

def test_SARA():
    saturates, aromatics, resins, asphaltenes = sara_totals(FullOil)

    assert [saturates, aromatics, resins, asphaltenes] == [0.38, 0.31,
                                                           0.16, 0.15]


def test_max_water_emulsion():
    data = make_gnome_oil(FullOil)

    assert data['emulsion_water_fraction_max'] == 0.39787


def test_max_water_emulsion_estimated():
    data = make_gnome_oil(SparseOil)

    #assert isclose(data['emulsion_water_fraction_max'], 0.8383435, rel_tol=1e-4)
    # wish there was a better way than hard-coded values ...
    assert isclose(data['emulsion_water_fraction_max'], 0.838, rel_tol=1e-3)

def test_bullwinkle():
    data = make_gnome_oil(FullOil)

    #assert data['bullwinkle_fraction'] == 0.0 # removed Entrained from stable emulsions
    assert isclose(data['bullwinkle_fraction'], .165592, rel_tol=1e-4)


def test_bullwinkle_estimated():
    data = make_gnome_oil(SparseOil)

    assert isclose(data['bullwinkle_fraction'], 0.017067, rel_tol=1e-4)


def test_no_cuts_exception():
    sparse_oil = get_sparse_oil()
    sparse_oil.metadata.product_type = "Condensate"

    with pytest.raises(ValueError):
        _gnome_oil = make_gnome_oil(sparse_oil)


def test_frac_recovered_exception():
    full_oil = get_full_oil()

    full_oil.metadata.product_type = "Condensate"
    full_oil.sub_samples[0].distillation_data.fraction_recovered.value = 5

    with pytest.raises(ValueError):
        _gnome_oil = make_gnome_oil(full_oil)


def test_estimate_pour_point():
    sparse_oil = get_sparse_oil()

    pour_point = estimate_pour_point(sparse_oil)

    assert isclose(pour_point, 188.372, rel_tol=1e-4)


def test_solubility():
    data = make_gnome_oil(FullOil)

    assert data['solubility'] == 0
