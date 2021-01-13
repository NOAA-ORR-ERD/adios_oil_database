"""
tests for the Physical Properties computation code
"""

from pathlib import Path

# import pytest

from adios_db.models.oil.oil import Oil
from adios_db.computation.physical_properties import get_density_data

ExampleRecordFile = Path(__file__).parent.parent / "test_models" / "test_oil" / "ExampleFullRecord.json"

FullOil = Oil.from_file(ExampleRecordFile)

print(FullOil)


def test_get_density_data_defaults():
    dd = get_density_data(FullOil)

    print(dd)

    assert len(dd) == 2

    assert dd[0] == (939.88, 273.15)
    assert dd[1] == (925.26, 288.15)


def test_get_density_data_units():
    dd = get_density_data(FullOil, density_units='g/cm^3', temp_units='C')

    print(dd)

    assert len(dd) == 2

    assert dd[0] == (.93988, 0.0)
    assert dd[1] == (.92526, 15.0)


