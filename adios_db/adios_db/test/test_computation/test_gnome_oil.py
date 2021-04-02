"""
tests for making a GNOME Oil

"""

from pathlib import Path
from math import isclose
import pytest
pytest.importorskip("scipy.optimize")

from adios_db.models.oil.oil import Oil
from adios_db.computation.gnome_oil import make_gnome_oil

ExampleRecordFile = Path(__file__).parent.parent / "test_models" / "test_oil" / "ExampleFullRecord.json"

FullOil = Oil.from_file(ExampleRecordFile)


def test_metadata():
    """
    does it get the basic metadata right?
    """
    data = make_gnome_oil(FullOil)

    # print(FullOil.metadata)

    assert data['name'] == FullOil.metadata.name
    assert data['api'] == FullOil.metadata.API
    assert data['adios_oil_id'] == "EC002234"


def test_physical_properties():

    data = make_gnome_oil(FullOil)

    assert isclose(data['flash_point'], 268.15)
    assert isclose(data['pour_point'], 248.15)


def test_densities():

    data = make_gnome_oil(FullOil)

    assert list(data['densities']) == [939.88, 925.26]
    assert list(data['density_ref_temps']) == [273.15, 288.15]
    assert list(data['density_weathering']) == [0.0, 0.0]








