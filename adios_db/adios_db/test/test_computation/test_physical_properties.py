"""
tests for the Physical Properties computation code
"""
from math import isclose
from pathlib import Path

import numpy as np
import pytest

import nucos

from adios_db.models.common import measurement as meas

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.physical_properties import DensityPoint

from adios_db.computation.physical_properties import bullwinkle_fraction
from adios_db.computation.physical_properties import (
    get_density_data,
    get_kinematic_viscosity_data,
    get_dynamic_viscosity_data,
    KinematicViscosity,
    Density,
    get_frac_recovered,
    max_water_fraction_emulsion,
    emul_water,
    get_interfacial_tension_water,
    get_interfacial_tension_seawater,
    convert_dvisc_to_kvisc,
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

    assert len(dd) == 2
    assert dd[0] == (939.88, 273.15)
    assert dd[1] == (925.26, 288.15)


def test_get_density_data_units():
    dd = get_density_data(FullOil, units='g/cm^3', temp_units='C')

    assert len(dd) == 2
    assert dd[0] == (.93988, 0.0)
    assert dd[1] == (.92526, 15.0)


def test_get_kinematic_viscosity_data_defaults():
    kv = get_kinematic_viscosity_data(FullOil)

    assert len(kv) == 2

    assert isclose(kv[0][0], .001383155, rel_tol=1e-6)  # kvisc
    assert isclose(kv[0][1], 273.15, rel_tol=1e-6)  # temp
    assert isclose(kv[1][0], .000378272, rel_tol=1e-6)  # kvisc
    assert isclose(kv[1][1], 288.15, rel_tol=1e-6)  # temp


def test_get_dynamic_viscosity_data_multiple_shear_rates_default():
    oil = Oil.from_file(
        EXAMPLE_DATA_DIR / "Record_with_viscosity_at_two_shear_rates.json"
    )
    dv = get_dynamic_viscosity_data(oil)

    print(oil.oil_id)

    assert len(dv) == 2

    print(dv)

    assert isclose(dv[0][0], 6.402, rel_tol=1e-6)  # dvisc
    assert isclose(dv[0][1], 275.15, rel_tol=1e-6)  # temp
    assert isclose(dv[1][0], 1.199, rel_tol=1e-6)  # dvisc
    assert isclose(dv[1][1], 288.15, rel_tol=1e-6)  # temp


def test_get_dynamic_viscosity_data_multiple_shear_rates_set():
    oil = Oil.from_file(
        EXAMPLE_DATA_DIR / "Record_with_viscosity_at_two_shear_rates.json"
    )
    dv = get_dynamic_viscosity_data(oil, shear_rate=100)

    print(oil.oil_id)

    assert len(dv) == 2

    print(dv)

    assert isclose(dv[0][0], 1.954, rel_tol=1e-6)  # dvisc
    assert isclose(dv[0][1], 275.15, rel_tol=1e-6)  # temp
    assert isclose(dv[1][0], 0.582, rel_tol=1e-6)  # dvisc
    assert isclose(dv[1][1], 288.15, rel_tol=1e-6)  # temp

def test_get_kinematic_viscosity_data_no_data():
    """
    Issue:
      https://gitlab.orr.noaa.gov/gnome/oil_database/oil_database/-/issues/544

    - Seemed to be getting 1.0 instead of nothing!
    - Error observed with record: EC00622

    - Hmm, turns out it works.  It was an error in the Generic Oil code
      that was using this.

    But keeping the test anyway -- why risk a regression?
    """
    oil = Oil.from_file(EXAMPLE_DATA_DIR / 'EC00622-no-visc.json')
    kv = get_kinematic_viscosity_data(oil)

    assert kv == []


# def test_get_kinematic_viscosity_data_from_dynamic():
#     """
#     There seemed to be an error with computing the kinematic
#     from the dynamic viscosity

#     """
#     oil = Oil.from_file(
#         EXAMPLE_DATA_DIR / 'record_with_only_dynamic_viscosity.json'
#     )
#     kv = get_kinematic_viscosity_data(oil)

#     print(kv)

#     assert kv == []

def test_convert_dvisc_to_kvisc():
    """
    make sure the conversion is correct

    """
    oil = Oil.from_file(
        EXAMPLE_DATA_DIR / 'record_with_only_dynamic_viscosity.json'
    )

    # dvis = get_dynamic_viscosity_data(oil)

    dvis = [(0.043000000000000003, 275.15),  # 2C
            (0.012, 288.15),  # 15C
            (0.0054, 323.15)]  # 50C
    print(dvis)

    print(get_density_data(oil, units='kg/m^3', temp_units="K"))
    # density = Density(oil)
    density = Density([(885.0, 288.15)])  # 15C

    # [(980.0, 288.15), (990.0, 273.15)])

    # 0.885, "unit": "g/cm^3",
    print(density.at_temp(15, 'C'))

    kvis = convert_dvisc_to_kvisc(dvis, density)

    print(kvis)

    # why would temp have changed?
    for kv, dv in zip(kvis, dvis):
        assert kv[1] == dv[1]
        kv2 = dv[0] / density.at_temp(dv[1], 'K')
        assert kv[0] == kv2


# @pytest.mark.xfail
def test_convert_dvisc_to_kvisc_from_record():
    """
    This is bit of an integration test

    For a record with only dynamic viscosity data, do we get the
    right kinematic viscosity?

    from the record::

    raw_dvis=[(43.0, 275.15), (5.4, 323.15)]

    """
    oil = Oil.from_file(
        EXAMPLE_DATA_DIR / 'record_with_only_dynamic_viscosity.json'
    )

    raw_dvis = get_dynamic_viscosity_data(oil, units="cP")
    print(f"{raw_dvis=}")

    density = Density(oil)

    kvis_data = get_kinematic_viscosity_data(oil)
    print(f"{kvis_data=}")

    kv = KinematicViscosity(oil)

    for dv in raw_dvis:
        print(f"{dv=}")
        kv2 = kv.at_temp(dv[1], kvis_units='cSt', temp_units='K')
        d = density.at_temp(dv[1], unit='K') / 1000
        dv2 = kv2 * d
        print(f"temp is: {nucos.convert('K', 'C', dv[1])} C")
        print(d)
        assert isclose(dv2, dv[0])


def test_get_dynamic_viscosity_data_defaults():
    dv = get_dynamic_viscosity_data(FullOil)

    assert len(dv) == 2

    assert isclose(dv[0][0], 1.3)
    assert isclose(dv[0][1], 273.15)
    assert isclose(dv[1][0], .35)
    assert isclose(dv[1][1], 288.15)


def test_get_dynamic_viscosity_data_units():
    dv = get_dynamic_viscosity_data(FullOil, units="poise", temp_units="C")

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

        assert dc.k_rho_default == k_rho

    def test_initiliaze_two_densities(self):
        oil = self.make_oil_with_densities([980.0, 990.0], [288.15, 268.15])
        dc = Density(oil)

        assert isclose(dc.k_rho_default, -0.5)

    def test_initiliaze_three_plus_densities(self):
        oil = self.make_oil_with_densities([982, 984, 991], [288, 278, 268])
        dc = Density(oil)

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


class TestKinematicViscosity:
    kv = KinematicViscosity(FullOil)

    def test_initilization(self):
        assert len(self.kv.kviscs) == 2
        assert len(self.kv.temps) == 2

    def test_values_at_known_temps(self):
        assert self.kv.kviscs
        assert isclose(self.kv.at_temp(273.15), 0.001383, rel_tol=1e-3)
        assert isclose(self.kv.at_temp(288.15), 0.0003783, rel_tol=1e-3)

    def test_no_data(self):
        """
        this record has no viscosity data -- should raise
        """
        oil = Oil.from_file(EXAMPLE_DATA_DIR / 'EC00622-no-visc.json')

        with pytest.raises(ValueError):
            _ = KinematicViscosity(oil)

#    def test_get_visc_data_multiple_shear_rates(self):



#    @pytest.mark.xfail
    def test_from_raw_data(self):
        # two data points should be an exact fit at the points
        data = [(0.043, 275.15),  # 2C
                (0.0054, 323.15)]  # 50C

        kv = KinematicViscosity(data)

        k2 = kv.at_temp(2, kvis_units='m^2/s', temp_units="C")
        assert isclose(k2, 0.043, rel_tol=1e-4)
        k50 = kv.at_temp(50, kvis_units='m^2/s', temp_units="C")
        assert isclose(k50, 0.0054, rel_tol=1e-4)

        # intermediate temp should be in between
        k20 = kv.at_temp(20, kvis_units='m^2/s', temp_units="C")
        assert k50 < k20 < k2

    def test_get_default_kv2_crude(self):
        """
        The curve:

        v = A exp(k_v2 / T)

        There's a default if there's only one data point
        """

        kv2 = KinematicViscosity.default_kv2(899.0, "Crude Oil NOS")

        # assuming value currently calculated is correct.
        assert np.isclose(kv2, 6211.103, rtol=1e-4)

    def test_get_default_kv2_bad_product_type(self):
        """
        The curve:

        v = A exp(k_v2 / T)

        There's a default if there's only one data point
        """
        with pytest.raises(TypeError, match="Unable to estimate kv2"):
            _kv2 = KinematicViscosity.default_kv2(899.0, "Refined Product NOS")

    def test_set_kv2(self):
        """
        The curve:

        v = A exp(k_v2 / T)

        Is fit to two or more data points. If only one is provided,
        then k_v2 must be assumed.

        This is testing that it works to specify it.
        """
        # one data point should be an exact fit at that point
        data = [
                # (0.043, 275.15),  # 2C
                (0.0054, 323.15),  # 50C
                ]

        data2 = [
                (0.043, 275.15),  # 2C
                (0.0054, 323.15),  # 50C
                ]

        # not specified -- uses the default default :-),
        # requires either multiple viscosities or k_v2 supplied,
        # should fail with one viscosity and no k_v2
        with pytest.raises(ValueError):
            _kv1 = KinematicViscosity(data)
        kv1 = KinematicViscosity(data2)
        kv2 = KinematicViscosity(data, k_v2=3000.0)

        # calculated from above data:
        # kv._k_v2=3843.3410327682077
        # kv._visc_A=3.691227309345265e-08

        # with the default and only the 50C point
        # kv._k_v2=2100.0
        # kv._visc_A=8.130513951017499e-06

        print(f"{kv2._k_v2=}")
        print(f"{kv2._visc_A=}")

        # assert kv1._k_v2 == KinematicViscosity.DEFAULT_KV2
        assert isclose(kv1._k_v2, 3843.341, rel_tol=1.e-4)
        assert kv2._k_v2 == 3000.0

        k1_2 = kv1.at_temp(2, kvis_units='m^2/s', temp_units="C")
        k2_2 = kv2.at_temp(2, kvis_units='m^2/s', temp_units="C")
        # assert isclose(k1_2, 0.043, rel_tol=1e-4)

        # both should match the one point provided
        k1_50 = kv1.at_temp(50, kvis_units='m^2/s', temp_units="C")
        k2_50 = kv2.at_temp(50, kvis_units='m^2/s', temp_units="C")
        assert isclose(k2_50, 0.0054, rel_tol=1e-4)

        # intermediate temp should be in between
        k1_20 = kv1.at_temp(20, kvis_units='m^2/s', temp_units="C")
        k2_20 = kv2.at_temp(20, kvis_units='m^2/s', temp_units="C")
        assert k1_50 < k1_20 < k1_2
        assert k2_50 < k2_20 < k2_2

    def test_one_viscosity_diesel(self):
        """
        if there's only one viscosity, and it's a diesel
        it should use the correct kv_2
        """
        oil = Oil.from_file(EXAMPLE_DATA_DIR / 'SimpleULSFO.json')

        kvisc = KinematicViscosity(oil)
        print(f"{kvisc.kviscs=}")
        print(f"{kvisc.temps=}")

        print(kvisc._k_v2)
        # assert kv._k_v2 == 6200.0 # switched default
        assert isclose(kvisc._k_v2, 3840.864, rel_tol=1e-4)

        assert isclose(kvisc.at_temp(kvisc.temps[0], 'm^2/s', 'K'),
                       kvisc.kviscs[0])
        t0 = kvisc.at_temp(0, 'cSt', 'C')
        t15 = kvisc.at_temp(15, 'cSt', 'C')
        t30 = kvisc.at_temp(30, 'cSt', 'C')

        print(t0, t15, t30)

        assert t0 > t15 > t30

    def test_one_viscosity_gasoline(self):
        """
        This was a bug with gasoline records

        """
        oil = Oil.from_file(EXAMPLE_DATA_DIR / 'AD00092_gasoline_one_viscosity.json')

        kvisc = KinematicViscosity(oil)
        print(f"{kvisc.kviscs=}")
        print(f"{kvisc.temps=}")

        print(f"{kvisc._k_v2=}")
        # assert kv._k_v2 == 6200.0 # switched default
        # assert isclose(kvisc._k_v2, 3792.73, rel_tol=1e-4)

        assert isclose(kvisc.at_temp(kvisc.temps[0], 'm^2/s', 'K'),
                       kvisc.kviscs[0])
        t0 = kvisc.at_temp(0, 'cSt', 'C')
        t15 = kvisc.at_temp(15, 'cSt', 'C')
        t30 = kvisc.at_temp(30, 'cSt', 'C')

        print(t0, t15, t30)

        assert t0 > t15 > t30


    def test_multiple_vicosities_crude(self):
        """
        if there's there's multiple viscosities, it shouldn't use any of the
        defaults
        """
        oil = Oil.from_file(EXAMPLE_DATA_DIR / 'hoops-blend_EX00026.json')

        kv = KinematicViscosity(oil)

        print(kv._k_v2)
        # This has multiple data points, it should not use any of the
        # default values.
        # for kv_2 in KinematicViscosity.default_kvs.values():
        #     assert kv._k_v2 != kv_2

        density = Density(oil).at_temp(288.15)  # 15C
        assert kv._k_v2 != kv.default_kv2(density, oil.metadata.product_type)

    def test_single_vicosities_crude(self):
        """
        if there's only one viscocity, and it's a Crude
        it should use the correct kv_2

        FIXME: any reason to test this??
        """
        oil = Oil.from_file(EXAMPLE_DATA_DIR / 'ExampleSparseRecord.json')

        kv = KinematicViscosity(oil)

        print(kv._k_v2)

        # assert kv._k_v2 == (KinematicViscosity
        #                     .default_kvs[oil.metadata.product_type])
        density = Density(oil).at_temp(288.15)  # 15C
        assert kv._k_v2 == kv.default_kv2(density, oil.metadata.product_type)

    def test_default_kv2_condensate(self):
        density = 800
        kv2 = self.kv.default_kv2(density, 'Condensate')

        # eyeballed off plot -- looks about right
        assert isclose(kv2, 10102.173958)

        density = 720
        kv2 = self.kv.default_kv2(density, 'Condensate')

        assert isclose(kv2, 993.672059)

    def test_default_kv2_distillate(self):
        density = 900
        kv2 = self.kv.default_kv2(density, "Distillate Fuel Oil")

        # eyeballed off plot -- looks about right
        assert isclose(kv2, 6581.2543244)

        density = 720
        kv2 = self.kv.default_kv2(density, "Distillate Fuel Oil")

        assert kv2 >= KinematicViscosity.slope_intercept_kv2["Distillate Fuel Oil"][2]


def test_get_frac_recovered():
    frac_recovered = get_frac_recovered(FullOil)

    assert frac_recovered[0] == 1.0

    frac_recovered = get_frac_recovered(SparseOil)

    assert frac_recovered[0] is None


def test_max_water_fraction_emulsion():
    y_max = max_water_fraction_emulsion(FullOil)

    assert y_max == 0.39787


def test_max_water_emulsion_no_estimation():
    sparse_oil = get_sparse_oil()

    sparse_oil.metadata.product_type = "Condensate"
    y_max = max_water_fraction_emulsion(sparse_oil)

    assert y_max is None


def test_max_water_estimation():
    y_max = emul_water(FullOil)

    assert isclose(y_max, 0.714749, rel_tol=1e-4)


def test_bullwinkle_estimated_non_crude():
    sparse_oil = get_sparse_oil()
    sparse_oil.metadata.product_type = "Condensate"
    bullwinkle = bullwinkle_fraction(sparse_oil)

    assert bullwinkle == 1.0


def test_bullwinkle_estimated_ni_va():
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
