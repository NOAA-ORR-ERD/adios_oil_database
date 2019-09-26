'''
    Test our main Cut model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Cut


class TestCut():
    @pytest.mark.parametrize('fraction, vapor_temp',
                             [
                              ({'value': 0.1, 'unit': '1'},
                               {'value': 15.0, 'unit': 'C'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 0.1, 'unit': '1'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 0.1, 'unit': '1'}, 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, fraction, vapor_temp):
        if fraction is None and vapor_temp is None:
            obj = Cut()
        elif vapor_temp is None:
            obj = Cut(fraction=fraction)
        if fraction is None:
            obj = Cut(vapor_temp=vapor_temp)
        else:
            obj = Cut(fraction=fraction, vapor_temp=vapor_temp)

        assert obj.fraction.value == float(fraction['value'])
        assert obj.fraction.unit == str(fraction['unit'])

        assert obj.vapor_temp.value == float(vapor_temp['value'])
        assert obj.vapor_temp.unit == str(vapor_temp['unit'])

    def test_init_defaults(self):
        obj = Cut(fraction={'value': 0.1, 'unit': '1'},
                  vapor_temp={'value': 15.0, 'unit': 'C'})

        assert obj.liquid_temp is None
        assert obj.weathering == 0.0
        assert obj.method is None

    @pytest.mark.parametrize('liquid_temp, weathering, method',
                             [
                              ({'value': 15.0, 'unit': 'C'}, 0.1, 'Method'),
                              ({'value': 15.0, 'unit': 'C'}, '0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 0.1, 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 15.0, 'unit': 'C'},
                                  'nope',
                                  'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 15.0, 'unit': 'C'},
                                  0.1,
                                  'LongMethod'
                                  '123456789 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, liquid_temp, weathering, method):
        obj = Cut(fraction={'value': 0.1, 'unit': '1'},
                  vapor_temp={'value': 15.0, 'unit': 'C'},
                  liquid_temp=liquid_temp,
                  weathering=weathering,
                  method=method)

        assert obj.liquid_temp.value == float(liquid_temp['value'])
        assert obj.liquid_temp.unit == str(liquid_temp['unit'])

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
