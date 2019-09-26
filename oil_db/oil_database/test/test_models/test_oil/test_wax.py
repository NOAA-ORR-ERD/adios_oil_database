'''
    Test our main Wax model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Wax


class TestWax():
    @pytest.mark.parametrize('fraction',
                             [
                              {'value': 0.1, 'unit': '1'},
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, fraction):
        if fraction is None:
            obj = Wax()
        else:
            obj = Wax(fraction=fraction)

        assert obj.fraction.value == float(fraction['value'])
        assert obj.fraction.unit == str(fraction['unit'])

    def test_init_defaults(self):
        # everything has a default
        obj = Wax(fraction={'value': 0.1, 'unit': '1'})

        assert obj.weathering == 0.0

        assert obj.method is None
        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, replicates, std_dev, method',
                             [
                              (0.1, 3.0, 0.2, 'Method'),
                              ('0.1', '3.0', '0.2', 0xdeadbeef),
                              pytest.param(
                                  'nope', 3.0, 0.2, 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'nope', 0.2, 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3.0, 'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3.0, 0.2, 'MethodNameTooLong',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, replicates, std_dev, method):
        obj = Wax(fraction={'value': 0.1, 'unit': '1'},
                  weathering=weathering,
                  replicates=replicates,
                  standard_deviation=std_dev,
                  method=method)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
        assert obj.method == str(method)
