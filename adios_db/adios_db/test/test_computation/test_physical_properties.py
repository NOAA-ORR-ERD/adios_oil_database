"""
tests for the Physical Properties computation code
"""

from math import isclose
from pathlib import Path

# import pytest

from adios_db.models.oil.oil import Oil
from adios_db.computation.physical_properties import (get_density_data,
                                                      get_kinematic_viscosity_data,
                                                      get_dynamic_viscosity_data,
                                                      density_at_temp,
                                                      KinematicViscosity
                                                      )


ExampleRecordFile = Path(__file__).parent.parent / "test_models" / "test_oil" / "ExampleFullRecord.json"

FullOil = Oil.from_file(ExampleRecordFile)


def test_get_density_data_defaults():
    dd = get_density_data(FullOil)

    print(dd)

    assert len(dd) == 2

    assert dd[0] == (939.88, 273.15)
    assert dd[1] == (925.26, 288.15)


def test_get_density_data_units():
    dd = get_density_data(FullOil, units='g/cm^3', temp_units='C')

    print(dd)

    assert len(dd) == 2

    assert dd[0] == (.93988, 0.0)
    assert dd[1] == (.92526, 15.0)


def test_get_kinematic_viscosity_data_defaults():
    kv = get_kinematic_viscosity_data(FullOil)

    print(kv)

    assert len(kv) == 2

    assert isclose(kv[0][0], 1383.155, rel_tol=1e-6)
    assert isclose(kv[0][1], 273.15, rel_tol=1e-6)
    assert isclose(kv[1][0], 378.272, rel_tol=1e-6)
    assert isclose(kv[1][1], 288.15, rel_tol=1e-6)


def test_get_dynamic_viscosity_data_defaults():
    dv = get_dynamic_viscosity_data(FullOil)

    print(dv)

    assert len(dv) == 2
    assert isclose(dv[0][0], 1.3)
    assert isclose(dv[0][1], 273.15)
    assert isclose(dv[1][0], .35)
    assert isclose(dv[1][1], 288.15)


def test_get_dynamic_viscosity_data_units():
    dv = get_dynamic_viscosity_data(FullOil, units="poise", temp_units="C")

    print(dv)

    assert len(dv) == 2
    assert dv[0] == (13.0, 0.0)
    assert dv[1] == (3.50, 15.0)


def test_density_at_temp():
    densities = [(980.0, 288.15),
                 (990, 273.15)]

    assert density_at_temp(densities, 288.15) == 980.0
    assert density_at_temp(densities, 273.15) == 990.0

class Test_KinematicViscosity:

    kv = KinematicViscosity(FullOil)

    def test_initilization(self):
        print(self.kv.kviscs)
        print(self.kv.temps)

        assert len(self.kv.kviscs) == 2
        assert len(self.kv.temps) == 2

    def test_values_at_known_temps(self):
        assert self.kv.kviscs
        assert isclose(self.kv.at_temp(273.15), 1383.0, rel_tol=1e-3)
        assert isclose(self.kv.at_temp(288.15), 378.3, rel_tol=1e-3)




