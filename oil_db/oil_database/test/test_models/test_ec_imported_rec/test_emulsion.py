'''
    Test our Environment Canada Emulsion model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECEmulsion


class TestECEmulsion():
    @pytest.mark.parametrize('water_content_percent, ref_temp_c, age_days',
                             [
                              (10.0, 15.0, 5.0),
                              ('10.0', '15.0', '5.0'),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 5.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 15.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 15.0, 5.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, None, 5.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 15.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope', 15.0, 5.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 'nope', 5.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 15.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, water_content_percent, ref_temp_c, age_days):
        if (water_content_percent is None and
                ref_temp_c is None and
                age_days is None):
            obj = ECEmulsion()
        elif ref_temp_c is None and age_days is None:
            obj = ECEmulsion(water_content_percent=water_content_percent)
        elif water_content_percent is None and age_days is None:
            obj = ECEmulsion(ref_temp_c=ref_temp_c)
        elif water_content_percent is None and ref_temp_c is None:
            obj = ECEmulsion(age_days=age_days)
        elif water_content_percent is None:
            obj = ECEmulsion(ref_temp_c=ref_temp_c, age_days=age_days)
        elif ref_temp_c is None:
            obj = ECEmulsion(water_content_percent=water_content_percent,
                             age_days=age_days)
        elif age_days is None:
            obj = ECEmulsion(water_content_percent=water_content_percent,
                             ref_temp_c=ref_temp_c)
        else:
            obj = ECEmulsion(water_content_percent=water_content_percent,
                             ref_temp_c=ref_temp_c,
                             age_days=age_days)

        assert obj.water_content_percent == float(water_content_percent)
        assert obj.ref_temp_c == float(ref_temp_c)
        assert obj.age_days == float(age_days)

    def test_init_defaults(self):
        obj = ECEmulsion(water_content_percent=10.0,
                         ref_temp_c=15.0,
                         age_days=7)

        assert obj.weathering == 0.0

        assert obj.wc_standard_deviation is None
        assert obj.wc_replicates is None

        assert obj.visual_stability is None

        assert obj.complex_modulus_pa is None
        assert obj.cm_standard_deviation is None

        assert obj.storage_modulus_pa is None
        assert obj.sm_standard_deviation is None

        assert obj.loss_modulus_pa is None
        assert obj.lm_standard_deviation is None

        assert obj.tan_delta_v_e is None
        assert obj.td_standard_deviation is None

        assert obj.complex_viscosity_pa_s is None
        assert obj.cv_standard_deviation is None

        assert obj.mod_replicates is None

    @pytest.mark.parametrize('weathering, visual_stability',
                             [
                              (0.1, 'Stable'),
                              ('0.1', 'Stable'),
                              pytest.param(
                                  'nope', 'Stable',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'NotAnEnum',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, visual_stability):
        obj = ECEmulsion(water_content_percent=10.0,
                         ref_temp_c=15.0, age_days=7,
                         weathering=weathering,
                         visual_stability=visual_stability)

        assert obj.weathering == float(weathering)
        assert obj.visual_stability == str(visual_stability)
