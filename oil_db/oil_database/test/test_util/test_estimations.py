'''
    Unit tests for the primitive oil property estimation methods.

    Note: We really should have data inputs and expected outputs that have been
          vetted by subject matter experts in this section.  But we will try
          to be as complete as we can for now.
'''
import pytest

import numpy as np

from oil_database.util.estimations import (density_from_api,
                                           api_from_density,
                                           density_at_temp,
                                           vol_expansion_coeff,
                                           specific_gravity,
                                           kvis_at_temp,
                                           resin_fraction,
                                           asphaltene_fraction,
                                           saturates_fraction,
                                           aromatics_fraction,
                                           _A_coeff,
                                           _B_coeff
                                           )


class TestDensity(object):
    @pytest.mark.parametrize('api, expected',
                             [(10.0, 1000.0),
                              ])
    def test_density_from_api(self, api, expected):
        assert np.isclose(density_from_api(api)[0], expected, rtol=0.001)

    @pytest.mark.parametrize('density, expected',
                             [(1000.0, 10.0),
                              ])
    def test_api_from_density(self, density, expected):
        assert np.isclose(api_from_density(density), expected, rtol=0.001)

    @pytest.mark.parametrize('ref_density, ref_temp_k, temp_k, k_rho_t, '
                             'expected',
                             [(1000.0, 288.15, 308.15, 0.0000, 1000.0),
                              (1000.0, 288.15, 289.15, 1.0, 500.0),
                              (1000.0, 288.15, 288.15, 0.0008, 1000.0),
                              (1000.0, 288.15, 278.15, 0.0008, 1008.86),
                              (1000.0, 288.15, 298.15, 0.0008, 992.06),
                              (1000.0, 288.15, 308.15, 0.0008, 984.25),
                              ])
    def test_density_at_temp(self, ref_density, ref_temp_k, temp_k, k_rho_t,
                             expected):
        assert np.isclose(density_at_temp(ref_density, ref_temp_k, temp_k,
                                          k_rho_t),
                          expected, rtol=0.001)

    @pytest.mark.parametrize('ref_density, ref_temp_k, temp_k, k_rho_t, ',
                             [(1000.0, 288.15, 287.15, 1.0),
                              (1000.0, 288.15, 286.15, 0.5),
                              (1000.0, 288.15, 284.15, 0.25),
                              ])
    def test_density_at_temp_div_error(self, ref_density, ref_temp_k, temp_k,
                                       k_rho_t):
        '''
            Basically, if there is a temperature difference equal to the
            inverse of the expansion coefficient, we will get a zero division
            error.  This is a bit unusual, as expansion coefficients tend to be
            pretty small, much smaller than the inverse of even a very large
            temperature delta.
            So I am not sure if we want to prevent this or not, and if so, how.
            So we will document it here.
        '''
        with pytest.raises(ZeroDivisionError):
            density_at_temp(ref_density, ref_temp_k, temp_k, k_rho_t)

    @pytest.mark.parametrize('rho_0, t_0, rho_1, t_1, expected',
                             [(1000.0, 288.15, 1000.0, 288.15, 0.0),
                              (1000.0, 288.15, 1000.0, 298.15, 0.0),
                              (1000.0, 288.15, 999.0, 298.15, 0.0001),
                              (1000.0, 288.15, 998.0, 298.15, 0.0002),
                              (1000.0, 288.15, 997.0, 298.15, 0.0003),
                              ])
    def test_expansion_coeff(self, rho_0, t_0, rho_1, t_1, expected):
        assert np.isclose(vol_expansion_coeff(rho_0, t_0, rho_1, t_1),
                          expected, rtol=0.001)

    @pytest.mark.parametrize('density, expected',
                             [(1000.0, 1.0),
                              (900.0, 0.9),
                              (800.0, 0.8),
                              ])
    def test_specific_gravity(self, density, expected):
        assert np.isclose(specific_gravity(density), expected, rtol=0.001)


class TestViscosity(object):
    @pytest.mark.parametrize('ref_kvis, ref_temp_k, temp_k, k_v2, expected',
                             [(1000.0, 288.15, 288.15, 2416.0, 1000.0),
                              (1000.0, 288.15, 298.15, 2416.0, 754.86),
                              (10000.0, 288.15, 298.15, 2416.0, 7548.6),
                              (1000.0, 288.15, 278.15, 2416.0, 1351.8),
                              (10000.0, 288.15, 278.15, 2416.0, 13518.0),
                              ])
    def test_kvis_at_temp(self, ref_kvis, ref_temp_k, temp_k, k_v2, expected):
        assert np.isclose(kvis_at_temp(ref_kvis, ref_temp_k, temp_k, k_v2),
                          expected, rtol=0.001)


class TestSARAFractions(object):
    @pytest.mark.parametrize('density, viscosity, f_other, expected',
                             [(1000.0, 1000.0, 0.0, 0.3373),
                              (1000.0, 10000.0, 0.0, 0.35735),
                              (1000.0, 10000.0, 0.8, 0.2),
                              ])
    def test_resin_fraction(self, density, viscosity, f_other, expected):
        assert np.isclose(resin_fraction(density, viscosity, f_other),
                          expected, rtol=0.0001)

    @pytest.mark.parametrize('density, viscosity, f_other, expected',
                             [(1000.0, 1000.0, 0.0, 0.2730),
                              (1000.0, 10000.0, 0.0, 0.3133),
                              (1000.0, 10000.0, 0.8, 0.2),
                              ])
    def test_asphaltene_fraction(self, density, viscosity, f_other, expected):
        assert np.isclose(asphaltene_fraction(density, viscosity, f_other),
                          expected, rtol=0.0001)

    @pytest.mark.parametrize('density, viscosity, f_other, expected',
                             [(1000.0, 1000.0, 0.0, 0.31865),
                              (1000.0, 10000.0, 0.0, 0.31866),
                              (1000.0, 10000.0, 0.8, 0.2),
                              ])
    def test_saturates_fraction(self, density, viscosity, f_other, expected):
        assert np.isclose(saturates_fraction(density, viscosity, f_other),
                          expected, rtol=0.0001)

    @pytest.mark.parametrize('f_res, f_asph, f_sat, expected',
                             [(0.0, 0.0, 0.0, 1.0),
                              (-1.0, -1.0, -1.0, 1.0),
                              (1.0, 1.0, 1.0, 0.0),
                              (0.3, 0.3, 0.3, 0.1),
                              ])
    def test_aromatics_fraction(self, f_res, f_asph, f_sat, expected):
        assert np.isclose(aromatics_fraction(f_res, f_asph, f_sat),
                          expected, rtol=0.0001)

    @pytest.mark.parametrize('density, expected',
                             [(500.0, 16.487),
                              (1000.0, 27.183),
                              (2000.0, 73.89),
                              ])
    def test_A_coeff(self, density, expected):
        assert np.isclose(_A_coeff(density), expected, rtol=0.0001)

    @pytest.mark.parametrize('density, viscosity, expected',
                             [(1000.0, 1000.0, 207.232),
                              (1000.0, 10000.0, 230.258),
                              ])
    def test_B_coeff(self, density, viscosity, expected):
        assert np.isclose(_B_coeff(density, viscosity), expected, rtol=0.0001)
