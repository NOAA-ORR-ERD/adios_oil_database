'''
    Test our main Kinematic Viscosity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import KVis


class TestKVis():
    @pytest.mark.parametrize('viscosity, ref_temp',
                             [
                              ({'value': 100.0, 'unit': 'cSt'},
                               {'value': 15.0, 'unit': 'C'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'cSt'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'cSt'}, 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, viscosity, ref_temp):
        if viscosity is None and ref_temp is None:
            obj = KVis()
        elif ref_temp is None:
            obj = KVis(viscosity=viscosity)
        elif viscosity is None:
            obj = KVis(ref_temp=ref_temp)
        else:
            obj = KVis(viscosity=viscosity, ref_temp=ref_temp)

        assert obj.viscosity.value == float(viscosity['value'])
        assert obj.viscosity.unit == str(viscosity['unit'])

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])

    def test_init_defaults(self):
        obj = KVis(viscosity={'value': 100.0, 'unit': 'cSt'},
                   ref_temp={'value': 15.0, 'unit': 'C'})

        assert obj.weathering == 0.0

    @pytest.mark.parametrize('weathering',
                             [
                              0.1,
                              '0.1',
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering):
        obj = KVis(viscosity={'value': 100.0, 'unit': 'cSt'},
                   ref_temp={'value': 15.0, 'unit': 'C'},
                   weathering=weathering)

        assert obj.weathering == float(weathering)
