'''
    Unit tests for the primitive oil property estimation methods.

    Note: We really should have data inputs and expected outputs that have been
          vetted by subject matter experts in this section.  But we will try
          to be as complete as we can for now.
'''
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
                                           _B_coeff,
                                           cut_temps_from_api,
                                           fmasses_from_cuts,
                                           fmasses_flat_dist,
                                           saturate_mol_wt,
                                           aromatic_mol_wt,
                                           resin_mol_wt,
                                           asphaltene_mol_wt,
                                           trial_densities,
                                           saturate_densities,
                                           aromatic_densities,
                                           resin_densities,
                                           asphaltene_densities,
                                           _hydrocarbon_characterization_param,
                                           refractive_index,
                                           _hydrocarbon_grouping_param,
                                           saturate_mass_fraction,
                                           pour_point_from_kvis,
                                           pour_point_from_sg_mw_kvis,
                                           flash_point_from_bp,
                                           flash_point_from_api,
                                           bullwinkle_fraction_from_asph,
                                           bullwinkle_fraction_from_api
                                           )

import pytest
pytestmark = pytest.mark.skipif(True, reason="Not using Estimations now")


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


class TestDistillation(object):
    @pytest.mark.parametrize('api, N, expected',
                             [(10.0, 1, [423.6, ]),
                              (10.0, 2, [423.6, 816.925]),
                              (10.0, 5,
                               [423.6, 580.93, 738.26, 895.59, 1052.92]),
                              ])
    def test_cut_temps_from_api(self, api, N, expected):
        assert np.allclose(cut_temps_from_api(api, N), expected, rtol=0.001)

    @pytest.mark.parametrize('f_evap_i, expected',
                             [([0.2, 0.4, 0.6, 0.8, 1.0],
                               [0.2, 0.2, 0.2, 0.2, 0.2]),
                              ])
    def test_fmasses_from_cuts(self, f_evap_i, expected):
        assert np.allclose(fmasses_from_cuts(f_evap_i), expected, rtol=0.001)

    @pytest.mark.parametrize('f_res, f_asph, N, expected',
                             [(0.2, 0.2, 1, [0.6, ]),
                              (0.2, 0.2, 2, [0.3, 0.3]),
                              (0.2, 0.2, 3, [0.2, 0.2, 0.2]),
                              ])
    def test_fmasses_flat_dist(self, f_res, f_asph, N, expected):
        assert np.allclose(fmasses_flat_dist(f_res, f_asph, N), expected,
                           rtol=0.001)


class TestComponentMolecularWeights(object):
    @pytest.mark.parametrize('boiling_point, expected',
                             [
                              ([300.0, 400.0, 500.0, 600.0, 700.0],
                               [68.352, 114.85, 178.12, 264.84, 387.21]),
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [178.124, 264.844, 387.21, 570.383, 878.967]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [178.124, 387.21, 878.967, 27851.2, 27851.2]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [178.124, 387.21, 878.967, 27851.2, 27851.2]),
                              ])
    def test_saturate_mol_wt(self, boiling_point, expected):
        '''
            FIXME: We need to verify the extremely big weights we are getting
                   for saturates at high temperatures.  They are about 100
                   times bigger than the lower temperatures.
        '''
        assert np.allclose(saturate_mol_wt(boiling_point), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_point, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [161.668, 246.226, 370.17, 567.587, 946.47]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [161.668, 370.17, 946.47, 23478.58, 23478.58]),
                              ])
    def test_aromatic_mol_wt(self, boiling_point, expected):
        '''
            FIXME: We need to verify the extremely big weights we are getting
                   for aromatics at high temperatures.  They are about 100
                   times bigger than the lower temperatures.
        '''
        assert np.allclose(aromatic_mol_wt(boiling_point), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_point, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [800.0, 800.0, 800.0, 800.0, 800.0]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [800.0, 800.0, 800.0, 800.0, 800.0]),
                              ])
    def test_resin_mol_wt(self, boiling_point, expected):
        assert np.allclose(resin_mol_wt(boiling_point), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_point, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [1000.0, 1000.0, 1000.0, 1000.0, 1000.0]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [1000.0, 1000.0, 1000.0, 1000.0, 1000.0]),
                              ])
    def test_asphaltene_mol_wt(self, boiling_point, expected):
        assert np.allclose(asphaltene_mol_wt(boiling_point), expected,
                           rtol=0.001)


class TestComponentDensities(object):
    @pytest.mark.parametrize('boiling_points, watson_factor, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0], 10.0,
                               [965.49, 1025.99, 1080.08, 1129.243, 1174.46]),
                              ([500.0, 600.0, 700.0, 800.0, 900.0], 12.0,
                               [804.57, 854.99, 900.069, 941.036, 978.717]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0], 10.0,
                               [965.49, 1080.08, 1174.46, 1255.707, 1327.614]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0], 12.0,
                               [804.57, 900.07, 978.717, 1046.422, 1106.345]),
                              ])
    def test_trial_densities(self, boiling_points, watson_factor, expected):
        assert np.allclose(trial_densities(boiling_points, watson_factor),
                           expected, rtol=0.001)

    @pytest.mark.parametrize('boiling_points, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [804.57, 854.99, 900.069, 941.036, 978.717]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [804.57, 900.07, 978.717, 1046.422, 1106.345]),
                              ])
    def test_saturate_densities(self, boiling_points, expected):
        assert np.allclose(saturate_densities(boiling_points), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_points, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [965.49, 1025.99, 1080.08, 1129.243, 1174.46]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [965.49, 1080.08, 1174.46, 1255.707, 1327.614]),
                              ])
    def test_aromatic_densities(self, boiling_points, expected):
        assert np.allclose(aromatic_densities(boiling_points), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_points, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [1100.0, 1100.0, 1100.0, 1100.0, 1100.0]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [1100.0, 1100.0, 1100.0, 1100.0, 1100.0]),
                              ])
    def test_resin_densities(self, boiling_points, expected):
        assert np.allclose(resin_densities(boiling_points), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('boiling_points, expected',
                             [
                              ([500.0, 600.0, 700.0, 800.0, 900.0],
                               [1100.0, 1100.0, 1100.0, 1100.0, 1100.0]),
                              ([500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [1100.0, 1100.0, 1100.0, 1100.0, 1100.0]),
                              ])
    def test_asphaltene_densities(self, boiling_points, expected):
        assert np.allclose(asphaltene_densities(boiling_points), expected,
                           rtol=0.001)


class TestHydrocarbonCharacterization(object):
    '''
        Note: I have little intuition in regards to whether these numbers
              are reasonable or not.  The inputs for mol_wt, SG, and temp_k
              are intended to be fairly reasonable.
    '''
    @pytest.mark.parametrize('SG, temp_k, expected',
                             [
                              (1.0, [500.0, 600.0, 700.0, 800.0, 900.0],
                               [0.32768, 0.32633, 0.32519,  0.3242, 0.32334]),
                              (1.0, [500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [0.32768, 0.32519, 0.32334, 0.32187, 0.32065]),
                              (0.9, [500.0, 600.0, 700.0, 800.0, 900.0],
                               [0.29746, 0.29623, 0.2952, 0.29431, 0.29352]),
                              (0.9, [500.0, 700.0, 900.0, 1100.0, 1300.0],
                               [0.29746, 0.2952, 0.29352, 0.29219, 0.29108]),
                              ])
    def test_hydrocarbon_characterization_param(self, SG, temp_k, expected):
        assert np.allclose(_hydrocarbon_characterization_param(SG, temp_k),
                           expected, rtol=0.001)

    @pytest.mark.parametrize('hc_char_param, expected',
                             [(1.0, np.inf),
                              (0.5, 2.0),
                              (-0.5, 0.0),
                              ([0.32768, 0.32633, 0.32519,  0.3242, 0.32334],
                               [1.5691, 1.5663, 1.5639, 1.5618, 1.56]),
                              ])
    def test_refractive_index(self, hc_char_param, expected):
        assert np.allclose(refractive_index(hc_char_param), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('mol_wt, SG, temp_k, expected',
                             [
                              ([178.124, 387.21, 878.967, 27851.2, 27851.2],
                               1.0,
                               [500.0, 600.0, 700.0, 800.0, 900.0],
                               [16.766, 35.339, 78.108, 2417.28, 2366.64]),
                              ])
    def test_hydrocarbon_grouping_param(self, mol_wt, SG, temp_k, expected):
        assert np.allclose(_hydrocarbon_grouping_param(mol_wt, SG, temp_k),
                           expected, rtol=0.001)


class TestComponentMassFractions(object):
    @pytest.mark.parametrize('fmass_i, mol_wt, SG, temp_k, expected',
                             [
                              ([0.2, 0.2, 0.2, 0.2, 0.2],
                               [68.352, 114.85, 178.124, 264.84, 387.21],
                               1.0,
                               [300.0, 400.0, 500.0, 600.0, 700.0],
                               [0.038196, 0.030496, 0.020384, 0.0068947, 0.]),
                              ([0.2, 0.2, 0.2, 0.2, 0.2],
                               [178.124, 387.21, 878.967, 27851.2, 27851.2],
                               1.0,
                               [500.0, 600.0, 700.0, 800.0, 900.0],
                               [0.020384, 0., 0., 0., 0.]),
                              ])
    def test_saturate_mass_fraction(self, fmass_i, mol_wt, SG, temp_k,
                                    expected):
        assert np.allclose(saturate_mass_fraction(fmass_i, mol_wt, SG, temp_k),
                           expected, rtol=0.001)


class TestPourPoint(object):
    @pytest.mark.parametrize('ref_kvis, ref_temp_k, expected',
                             [
                              (0.3, 288.15, 269.45),
                              ([0.55, 0.3, 0.17],
                               [278.15, 288.15, 298.15],
                               [269.2, 269.45, 269.66]),
                              ])
    def test_pour_point_from_kvis(self, ref_kvis, ref_temp_k, expected):
        '''
            Fixme: I am not sure if this function is producing good results.
                   To produce a credible pour point temperature, we need to
                   make the KVis pretty small it seems.
        '''
        assert np.allclose(pour_point_from_kvis(ref_kvis, ref_temp_k),
                           expected, rtol=0.001)

    @pytest.mark.parametrize('SG, mol_wt, kvis, expected',
                             [
                              (1.0, 1.0, 1.0, -2.35),  # baseline function args
                              (0.9, 30.352, 100.0, 266.97),
                              ])
    def test_pour_point_from_sg_mw_kvis(self, SG, mol_wt, kvis, expected):
        assert np.allclose(pour_point_from_sg_mw_kvis(SG, mol_wt, kvis),
                           expected, rtol=0.001)


class TestFlashPoint(object):
    @pytest.mark.parametrize('temp_k, expected',
                             [
                              (273.15, 305.47),
                              (288.15, 315.82),
                              (303.15, 326.17),
                              ([273.15, 288.15, 303.15],
                               [305.47, 315.82, 326.17])
                              ])
    def test_flash_point_from_bp(self, temp_k, expected):
        assert np.allclose(flash_point_from_bp(temp_k), expected, rtol=0.001)

    @pytest.mark.parametrize('api, expected',
                             [
                              (8.0, 430.28),
                              (9.0, 426.94),
                              (10.0, 423.6),
                              (11.0, 420.26),
                              (12.0, 416.92),
                              ([8.0, 9.0, 10.0, 11.0, 12.0],
                               [430.28, 426.94, 423.6, 420.26, 416.92])
                              ])
    def test_flash_point_from_api(self, api, expected):
        assert np.allclose(flash_point_from_api(api), expected, rtol=0.001)


class TestBullwinkle(object):
    @pytest.mark.parametrize('f_asph, expected',
                             [
                              (0.01, 0.2841),
                              (0.05, 0.1405),
                              (0.089, 0.00049),
                              (0.09, -0.0031),
                              (0.1, -0.039),
                              (0.15, -0.2185),
                              ])
    def test_bullwinkle_fraction_from_asph(self, f_asph, expected):
        '''
            Fixme: I don't think we should be getting negative fractions here.
        '''
        assert np.allclose(bullwinkle_fraction_from_asph(f_asph), expected,
                           rtol=0.001)

    @pytest.mark.parametrize('api, expected',
                             [
                              (8.0, -0.115),
                              (9.0, -0.08547),
                              (10.0, -0.0591),
                              (11.0, -0.03525),
                              (12.0, -0.01348),
                              ([8.0, 9.0, 10.0, 11.0, 12.0],
                               [-0.115, -0.08547, -0.0591, -0.03525, -0.01348])
                              ])
    def test_bullwinkle_fraction_from_api(self, api, expected):
        '''
            Fixme: I don't think we should be getting negative fractions here.
        '''
        assert np.allclose(bullwinkle_fraction_from_api(api), expected,
                           rtol=0.001)
