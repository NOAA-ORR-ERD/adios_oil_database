'''
    Test our main Emulsion model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Emulsion


class TestEmulsion():
    @pytest.mark.parametrize('water_content, ref_temp, age',
                             [
                              ({'value': 10.0, 'unit': '%'},
                               {'value': 15.0, 'unit': 'C'},
                               {'value': 5.0, 'unit': 'days'}),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, {'value': 5.0, 'unit': 'days'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None,
                                  {'value': 15.0, 'unit': 'C'},
                                  {'value': 5.0, 'unit': 'days'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'}, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'},
                                  None,
                                  {'value': 5.0, 'unit': 'days'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'},
                                  {'value': 15.0, 'unit': 'C'},
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope',
                                  {'value': 15.0, 'unit': 'C'},
                                  {'value': 5.0, 'unit': 'days'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'},
                                  'nope',
                                  {'value': 5.0, 'unit': 'days'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'},
                                  {'value': 15.0, 'unit': 'C'},
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, water_content, ref_temp, age):
        if (water_content is None and ref_temp is None and age is None):
            obj = Emulsion()
        elif ref_temp is None and age is None:
            obj = Emulsion(water_content=water_content)
        elif water_content is None and age is None:
            obj = Emulsion(ref_temp=ref_temp)
        elif water_content is None and ref_temp is None:
            obj = Emulsion(age=age)
        elif water_content is None:
            obj = Emulsion(ref_temp=ref_temp, age=age)
        elif ref_temp is None:
            obj = Emulsion(water_content=water_content,
                           age=age)
        elif age is None:
            obj = Emulsion(water_content=water_content,
                           ref_temp=ref_temp)
        else:
            obj = Emulsion(water_content=water_content,
                           ref_temp=ref_temp,
                           age=age)

        assert obj.water_content.value == float(water_content['value'])
        assert obj.water_content.unit == str(water_content['unit'])

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])

        assert obj.age.value == float(age['value'])
        assert obj.age.unit == str(age['unit'])

    def test_init_defaults(self):
        obj = Emulsion(water_content={'value': 10.0, 'unit': '%'},
                       ref_temp={'value': 15.0, 'unit': 'C'},
                       age={'value': 5.0, 'unit': 'days'})

        assert obj.weathering == 0.0

        assert obj.wc_standard_deviation is None
        assert obj.wc_replicates is None

        assert obj.visual_stability is None

        assert obj.complex_modulus is None
        assert obj.cm_standard_deviation is None

        assert obj.storage_modulus is None
        assert obj.sm_standard_deviation is None

        assert obj.loss_modulus is None
        assert obj.lm_standard_deviation is None

        assert obj.tan_delta_v_e is None
        assert obj.td_standard_deviation is None

        assert obj.complex_viscosity is None
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
        obj = Emulsion(water_content={'value': 10.0, 'unit': '%'},
                       ref_temp={'value': 15.0, 'unit': 'C'},
                       age={'value': 5.0, 'unit': 'days'},
                       weathering=weathering,
                       visual_stability=visual_stability)

        assert obj.weathering == float(weathering)
        assert obj.visual_stability == str(visual_stability)
