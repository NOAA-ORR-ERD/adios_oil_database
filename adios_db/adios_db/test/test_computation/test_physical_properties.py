"""
tests for the Physical Properties computation code
"""

from math import isclose
from pathlib import Path
import numpy as np
import pytest

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.physical_properties import DensityPoint
from adios_db.models.common import measurement as meas

from adios_db.computation.physical_properties import (get_density_data,
                                                      get_kinematic_viscosity_data,
                                                      get_dynamic_viscosity_data,
                                                      KinematicViscosity,
                                                      Density,
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

    assert isclose(kv[0][0], .001383155, rel_tol=1e-6)  # kvisc
    assert isclose(kv[0][1], 273.15, rel_tol=1e-6)  # temp
    assert isclose(kv[1][0], .000378272, rel_tol=1e-6)  # kvisc
    assert isclose(kv[1][1], 288.15, rel_tol=1e-6)  # temp


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


class TestDensity:
    """
    tests of the density class
    """
    def make_oil_with_densities(self, densities, temps):
        oil = Oil(oil_id = "DENSITY_TESTER")
        sample = Sample()
        sample.metadata.name = "only density"
        oil.sub_samples.append(sample)
        for d, t in zip(densities, temps):
            dp = DensityPoint(meas.Density(d, unit="kg/m^3"),
                              meas.Temperature(t, unit="K"))
            sample.physical_properties.densities.append(dp)
        return oil

    @pytest.mark.parametrize("density, temp, k_rho",
                             [(800, 288.16, -0.0009),
                              (990, 288.16, -0.0008),
                              (800, 293.0, -0.0009),  # a bit higher than 15C
                              (990, 285.0, -0.0008),  # a bit lower than 15C
                              (800, 294.0, -0.00085),  # much higher than 15C
                              (990, 283.00, -0.00085),  # much lower than 15C
                              ])
    def test_initiliaze_one_density(self, density, temp, k_rho):

        oil = self.make_oil_with_densities([density], [temp])
        dc = Density(oil)

        print(dc.k_rho_default)
        assert dc.k_rho_default == k_rho

    def test_initiliaze_two_densities(self):

        oil = self.make_oil_with_densities([980.0, 990.0], [288.15, 268.15])
        dc = Density(oil)

        print(dc.k_rho_default)

        assert isclose(dc.k_rho_default, -0.5)


    def test_initiliaze_three_plus_densities(self):

        oil = self.make_oil_with_densities([982, 984, 991], [288, 278, 268])
        dc = Density(oil)

        print(dc.k_rho_default)

        assert isclose(dc.k_rho_default, -0.45)

    def test_initilize_sort(self):
        """
        make sure the data are sorted when added
        """
        oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density(oil)

        assert dc.temps == (287.0, 288.0, 289.0)
        assert dc.densities == (990.0, 980.0, 985.0)

    def test_density_at_temp(self):

        # oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density([(980.0, 288.15),
                      (990.0, 273.15)])

        assert dc.at_temp(288.15) == 980.0
        assert dc.at_temp(273.15) == 990.0

    def test_density_at_temp_vector_exact(self):

        # oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density([(980.0, 288.15),
                      (990.0, 273.15),
                      (985.0, 280.0)])

        # densities = [(980.0, 288.15),
        #              (990.0, 273.15)]

        assert np.all(dc.at_temp((288.15, 273.15, 280.0))
                      == (980.0, 990.0, 985.0))

    def test_density_at_temp_vector_interp(self):

        # oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density([(990.0, 270.0),
                      (984.0, 280.0),
                      (980.0, 290.0),
                      ])

        # densities = [(980.0, 288.15),
        #              (990.0, 273.15)]


        print("k_rho_default:", dc.k_rho_default)

        D = dc.at_temp((275, 286))

        assert  984 < D[0] < 990
        assert  980 < D[1] < 984


    def test_density_at_temp_out_of_range(self):

        # oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density([(990.0, 270.0),
                      (985.0, 280.0),
                      (980.0, 290.0),
                      ])

        # densities = [(980.0, 288.15),
        #              (990.0, 273.15)]

        D = dc.at_temp((300, 260))

        assert  D[0] < 980
        assert  D[1] > 990

    def test_density_at_temp_single_out_of_range(self):

        # oil = self.make_oil_with_densities([980.0, 990.0, 985.0], [288, 287, 289])
        dc = Density([(990.0, 270.0),
                      ])

        D = dc.at_temp(260)

        assert  D  ==  990 - (10 * -0.00085)



class Test_KinematicViscosity:

    kv = KinematicViscosity(FullOil)

    def test_initilization(self):
        print(self.kv.kviscs)
        print(self.kv.temps)

        assert len(self.kv.kviscs) == 2
        assert len(self.kv.temps) == 2

    def test_values_at_known_temps(self):
        print(self.kv.kviscs)
        print(self.kv.temps)

        assert self.kv.kviscs
        assert isclose(self.kv.at_temp(273.15), 0.001383, rel_tol=1e-3)
        assert isclose(self.kv.at_temp(288.15), 0.0003783, rel_tol=1e-3)




