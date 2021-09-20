"""
tests for making a GNOME Oil

"""

from pathlib import Path
from math import isclose
import pytest
pytest.importorskip("scipy.optimize")

from adios_db.models.oil.oil import Oil
from adios_db.computation.gnome_oil import make_gnome_oil, sara_totals
from adios_db.computation.physical_properties import emul_water

HERE = Path(__file__).parent

EXAMPLE_DATA_DIR = HERE.parent / "data_for_testing" / "example_data"

full_oil_filename = EXAMPLE_DATA_DIR / "ExampleFullRecord.json"


# use the function if you're going to change the Oil object.
def get_full_oil():
    return Oil.from_file(full_oil_filename)

FullOil = get_full_oil()

# run it through the Oil object to make sure its up to date:
try:
    FullOil.to_file(full_oil_filename)
except: # in case the tests are running somewhere read-only
    pass


def test_metadata():
    """
    does it get the basic metadata right?
    """
    data = make_gnome_oil(FullOil)

    # print(FullOil.metadata)

    assert data['name'] == FullOil.metadata.name
    # the API might change
    #assert data['api'] == FullOil.metadata.API
    assert data['adios_oil_id'] == "EC02234"


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


def test_SARA():

    saturates, aromatics, resins, asphaltenes = sara_totals(FullOil)

    assert [saturates, aromatics, resins, asphaltenes] == [0.38, 0.31, .16, .15]


def test_max_water_emulsion():

    data = make_gnome_oil(FullOil)

    assert data['emulsion_water_fraction_max'] == .9


def test_emul_water():

    y_max = emul_water(FullOil)

    print ("y_max = ", y_max)
    assert y_max == .7147493538099328


def test_solubility():

    data = make_gnome_oil(FullOil)

    assert data['solubility'] == 0

# not being used -- we can add back if needed
# def test_k0y():

#     data = make_gnome_oil(FullOil)

#     assert data['k0y'] == 2.024e-06
