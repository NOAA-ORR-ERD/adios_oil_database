'''
    Test our Environment Canada Alkanes model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import NAlkanes


class TestECNAlkanes():
    def test_init_defaults(self):
        # basically everything has a default
        obj = NAlkanes()

        assert obj.weathering == 0.0
        assert obj.method is None
        assert obj.pristane is None
        assert obj.phytane is None
        assert obj.c8 is None
        assert obj.c9 is None
        assert obj.c10 is None
        assert obj.c11 is None
        assert obj.c12 is None
        assert obj.c13 is None
        assert obj.c14 is None
        assert obj.c15 is None
        assert obj.c16 is None
        assert obj.c17 is None
        assert obj.c18 is None
        assert obj.c19 is None
        assert obj.c20 is None
        assert obj.c21 is None
        assert obj.c22 is None
        assert obj.c23 is None
        assert obj.c24 is None
        assert obj.c25 is None
        assert obj.c26 is None
        assert obj.c27 is None
        assert obj.c28 is None
        assert obj.c29 is None
        assert obj.c30 is None
        assert obj.c31 is None
        assert obj.c32 is None
        assert obj.c33 is None
        assert obj.c34 is None
        assert obj.c35 is None
        assert obj.c36 is None
        assert obj.c37 is None
        assert obj.c38 is None
        assert obj.c39 is None
        assert obj.c40 is None
        assert obj.c41 is None
        assert obj.c42 is None
        assert obj.c43 is None
        assert obj.c44 is None

    @pytest.mark.parametrize('weathering, method, pristane',
                             [
                              (0.1, 'Method', {'value': 10.0, 'unit': 'ug/g'}),
                              ('0.1', 0xdeadbeef, {'value': 10.0,
                                                   'unit': 'ug/g'}),
                              pytest.param(
                                  'nope', 'Method',
                                  {'value': 10.0, 'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong',
                                  {'value': 10.0, 'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, pristane):
        # we will not test every attribute, just the ones that have
        # constraints
        obj = NAlkanes(weathering=weathering,
                       method=method,
                       pristane=pristane)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.pristane.value == float(pristane['value'])
        assert obj.pristane.unit == str(pristane['unit'])
