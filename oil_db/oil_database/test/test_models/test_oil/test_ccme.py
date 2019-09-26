'''
    Test our main CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import (CCMEFraction,
                                     CCMESaturateCxx,
                                     CCMEAromaticCxx,
                                     CCMETotalPetroleumCxx)


class TestCCMEFraction():
    def test_init_defaults(self):
        obj = CCMEFraction()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.f1 is None
        assert obj.f2 is None
        assert obj.f3 is None
        assert obj.f4 is None

    @pytest.mark.parametrize('weathering, method, f1',
                             [
                              (0.1, 'Method', {'value': 10.0, 'unit': 'ug/g'}),
                              ('0.1', 0xdeadbeef, {'value': 10.0,
                                                   'unit': 'ug/g'}),
                              pytest.param(
                                  'nope', 'Method', {'value': 10.0,
                                                     'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', {'value': 10.0,
                                                             'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, f1):
        obj = CCMEFraction(weathering=weathering,
                           method=method, f1=f1)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.f1.value == float(f1['value'])
        assert obj.f1.unit == str(f1['unit'])


class TestCCMESaturateCxx():
    def test_init_defaults(self):
        obj = CCMESaturateCxx()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.n_c8_to_n_c10 is None
        assert obj.n_c10_to_n_c12 is None
        assert obj.n_c12_to_n_c16 is None
        assert obj.n_c16_to_n_c20 is None
        assert obj.n_c20_to_n_c24 is None
        assert obj.n_c24_to_n_c28 is None
        assert obj.n_c28_to_n_c34 is None
        assert obj.n_c34 is None

    @pytest.mark.parametrize('weathering, method, n_c8_to_n_c10',
                             [
                              (0.1, 'Method', 10.0),
                              ('0.1', 0xdeadbeef, '10.0'),
                              pytest.param(
                                  'nope', 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, n_c8_to_n_c10):
        obj = CCMESaturateCxx(weathering=weathering,
                              method=method,
                              n_c8_to_n_c10=n_c8_to_n_c10)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.n_c8_to_n_c10 == float(n_c8_to_n_c10)


class TestCCMEAromaticCxx():
    def test_init_defaults(self):
        obj = CCMEAromaticCxx()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.n_c8_to_n_c10 is None
        assert obj.n_c10_to_n_c12 is None
        assert obj.n_c12_to_n_c16 is None
        assert obj.n_c16_to_n_c20 is None
        assert obj.n_c20_to_n_c24 is None
        assert obj.n_c24_to_n_c28 is None
        assert obj.n_c28_to_n_c34 is None
        assert obj.n_c34 is None

    @pytest.mark.parametrize('weathering, method, n_c8_to_n_c10',
                             [
                              (0.1, 'Method', 10.0),
                              ('0.1', 0xdeadbeef, '10.0'),
                              pytest.param(
                                  'nope', 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, n_c8_to_n_c10):
        obj = CCMEAromaticCxx(weathering=weathering,
                              method=method,
                              n_c8_to_n_c10=n_c8_to_n_c10)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.n_c8_to_n_c10 == float(n_c8_to_n_c10)


class TestCCMETotalPetroleumCxx():
    def test_init_defaults(self):
        obj = CCMETotalPetroleumCxx()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.n_c8_to_n_c10 is None
        assert obj.n_c10_to_n_c12 is None
        assert obj.n_c12_to_n_c16 is None
        assert obj.n_c16_to_n_c20 is None
        assert obj.n_c20_to_n_c24 is None
        assert obj.n_c24_to_n_c28 is None
        assert obj.n_c28_to_n_c34 is None
        assert obj.n_c34 is None

    @pytest.mark.parametrize('weathering, method, n_c8_to_n_c10',
                             [
                              (0.1, 'Method', 10.0),
                              ('0.1', 0xdeadbeef, '10.0'),
                              pytest.param(
                                  'nope', 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, n_c8_to_n_c10):
        obj = CCMETotalPetroleumCxx(weathering=weathering,
                                    method=method,
                                    n_c8_to_n_c10=n_c8_to_n_c10)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.n_c8_to_n_c10 == float(n_c8_to_n_c10)
