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
from adios_db.computation.physical_properties import bullwinkle_fraction
from adios_db.models.common import measurement as meas

from adios_db.computation.physical_properties import (get_density_data,
                                                      get_kinematic_viscosity_data,
                                                      get_dynamic_viscosity_data,
                                                      KinematicViscosity,
                                                      Density,
                                                      get_frac_recovered,
                                                      max_water_fraction_emulsion,
                                                      emul_water,
                                                      get_interfacial_tension_water,
                                                      get_interfacial_tension_seawater,
                                                      )


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
        oil = Oil(oil_id="DENSITY_TESTER")
        sample = Sample()
        sample.metadata.name = "only density"

        oil.sub_samples.append(sample)

        for d, t in zip(densities, temps):
            dp = DensityPoint(meas.Density(d, unit="kg/m^3"),
                              meas.Temperature(t, unit="K"))
            sample.physical_properties.densities.append(dp)

        return oil

    def test_initilization_zero_densities(self):
        """
        no density data -- ValueError trying to initilize a Density object
        """
        oil = self.make_oil_with_densities([], [])

        with pytest.raises(ValueError):
            _dc = Density(oil)

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
        oil = self.make_oil_with_densities([980.0, 990.0, 985.0],
                                           [288, 287, 289])
        dc = Density(oil)

        assert dc.temps == (287.0, 288.0, 289.0)
        assert dc.densities == (990.0, 980.0, 985.0)

    def test_density_at_temp(self):
        dc = Density([(980.0, 288.15),
                      (990.0, 273.15)])

        assert dc.at_temp(288.15) == 980.0
        assert dc.at_temp(273.15) == 990.0

    def test_density_at_temp_vector_exact(self):
        dc = Density([(980.0, 288.15),
                      (990.0, 273.15),
                      (985.0, 280.0)])

        assert np.all(dc.at_temp((288.15, 273.15, 280.0))
                      == (980.0, 990.0, 985.0))

    def test_density_at_temp_vector_interp(self):
        dc = Density([(990.0, 270.0),
                      (984.0, 280.0),
                      (980.0, 290.0),
                      ])

        print("k_rho_default:", dc.k_rho_default)

        D = dc.at_temp((275, 286))

        assert 984 < D[0] < 990
        assert 980 < D[1] < 984

    def test_density_at_temp_out_of_range(self):
        dc = Density([(990.0, 270.0),
                      (985.0, 280.0),
                      (980.0, 290.0),
                      ])

        D = dc.at_temp((300, 260))

        assert D[0] < 980
        assert D[1] > 990

    def test_density_at_temp_single_out_of_range(self):
        dc = Density([(990.0, 270.0),
                      ])

        D = dc.at_temp(260)

        assert D == 990 - (10 * -0.00085)

    def test_density_at_temp_single_20C(self):
        """
        there seemed to be an error when there was a single value at
        ref temp 20C (293.15K)

        Checking at 60F (288.716): used to compute API
        """
        dc = Density([(990.0, 293.15),
                      ])

        D = dc.at_temp(288.716)

        result = 990 + ((288.716 - 293.15) * -0.0008)

        assert D == result


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


def test_get_frac_recovered():
    frac_recovered = get_frac_recovered(FullOil)

    assert frac_recovered[0] == 1.0

    frac_recovered = get_frac_recovered(SparseOil)

    assert frac_recovered[0] ==  None

def test_max_water_fraction_emulsion():
    y_max = max_water_fraction_emulsion(FullOil)

    assert y_max == 0.39787


def test_max_water_emulsion_no_estimation():
    sparse_oil = get_sparse_oil()

    sparse_oil.metadata.product_type = "Condensate"
    y_max = max_water_fraction_emulsion(sparse_oil)

    assert y_max == None


def test_max_water_estimation():
    y_max = emul_water(FullOil)

    assert isclose(y_max, 0.714749, rel_tol=1e-4)


def test_bullwinkle_estimated_non_crude():
    sparse_oil = get_sparse_oil()
    sparse_oil.metadata.product_type = "Condensate"
    bullwinkle = bullwinkle_fraction(sparse_oil)

    assert bullwinkle == 1.0


def test_bullwinkle_estimated_ni_va():
    sparse_oil = get_sparse_oil()
    bullwinkle = bullwinkle_fraction(SparseOil)

    assert isclose(bullwinkle, 0.0171199, rel_tol=1e-4)


def test_bullwinkle_estimated_asph():
    full_oil = get_full_oil()
    bullwinkle = bullwinkle_fraction(full_oil)

    assert isclose(bullwinkle, 0.164338, rel_tol=1e-4)


def test_bullwinkle_estimated_api():
    full_oil = get_full_oil()
    full_oil.sub_samples[0].SARA.asphaltenes.value = 0
    bullwinkle = bullwinkle_fraction(full_oil)

    assert isclose(bullwinkle,  0.052838, rel_tol=1e-4)


def test_interfacial_tension_water():
    full_oil = get_full_oil()
    interfacial_tension = get_interfacial_tension_water(full_oil)

    assert isclose(interfacial_tension[0][0],  .024237, rel_tol=1e-4)


def test_interfacial_tension_seawater():
    full_oil = get_full_oil()
    interfacial_tension = get_interfacial_tension_seawater(full_oil)

    assert interfacial_tension[0][0] == .023827
