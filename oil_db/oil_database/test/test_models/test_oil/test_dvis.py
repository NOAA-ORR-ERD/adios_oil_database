'''
    Test our main Dynamic Viscosity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import DVis


class TestDVis():
    @pytest.mark.parametrize('viscosity, ref_temp',
                             [
                              ({'value': 100.0, 'unit': 'mPa s'},
                               {'value': 15.0, 'unit': 'C'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'mPa s'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'mPa s'}, 'bogus',
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
            obj = DVis()
        elif ref_temp is None:
            obj = DVis(viscosity=viscosity)
        elif viscosity is None:
            obj = DVis(ref_temp=ref_temp)
        else:
            obj = DVis(viscosity=viscosity, ref_temp=ref_temp)

        assert obj.viscosity.value == float(viscosity['value'])
        assert obj.viscosity.unit == str(viscosity['unit'])

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])

    def test_init_defaults(self):
        obj = DVis(viscosity={'value': 100.0, 'unit': 'mPa s'},
                   ref_temp={'value': 15.0, 'unit': 'C'})

        assert obj.weathering == 0.0
        assert obj.method is None
        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, method, replicates, std_dev',
                             [
                              (0.1, 'Method', '3', 0.01),
                              ('0.1', 0xdeadbeef, '3', '0.01'),
                              pytest.param(
                                  'nope', 'Method', 3, 0.01,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  3, 0.01,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope', 0.01,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 3, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, replicates, std_dev):
        obj = DVis(viscosity={'value': 100.0, 'unit': 'mPa s'},
                   ref_temp={'value': 15.0, 'unit': 'C'},
                   weathering=weathering,
                   method=method,
                   replicates=replicates,
                   standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
