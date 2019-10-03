'''
    Test our main Evaporation Equation model class
'''
import numpy as np

import pytest

from pydantic import ValidationError

from oil_database.models.oil import EvaporationEq


class TestEvaporationEq():
    @pytest.mark.parametrize('a, b, equation',
                             [
                              (1.0, 2.0, '(A + BT) ln t'),
                              ('1.0', '2.0', '(A + BT) ln t'),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope', 2.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 'nope', '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, a, b, equation):
        if a is None and b is None and equation is None:
            obj = EvaporationEq()
        elif b is None and equation is None:
            obj = EvaporationEq(a=a)
        elif a is None and equation is None:
            obj = EvaporationEq(b=b)
        elif a is None and b is None:
            obj = EvaporationEq(equation=equation)
        elif equation is None:
            obj = EvaporationEq(a=a, b=b)
        elif b is None:
            obj = EvaporationEq(a=a, equation=equation)
        elif a is None:
            obj = EvaporationEq(b=b, equation=equation)
        else:
            obj = EvaporationEq(a=a, b=b, equation=equation)

        assert obj.a == float(a)
        assert obj.b == float(b)
        assert obj.equation == str(equation)

    def test_init_defaults(self):
        obj = EvaporationEq(a=1.0, b=2.0, equation='(A + BT) ln t')

        assert obj.weathering == 0.0
        assert obj.c is None

    @pytest.mark.parametrize('c, weathering',
                             [
                              (1.0, 0.1),
                              ('1.0', '0.1'),
                              pytest.param(
                                  'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, c, weathering):
        obj = EvaporationEq(a=1.0, b=2.0, c=c, equation='(A + BT) ln t',
                            weathering=weathering)

        assert obj.weathering == float(weathering)
        assert obj.c == float(c)

    @pytest.mark.parametrize('equation, t, T, expected',
                             [
                              ('(A + BT) ln t', 1.3956125, 1.0, 1.0),
                              ('(A + BT) sqrt(t)', 1.0, 2.0, 5.0),
                              ('A + B ln (t + C)', 1.0, 2.0, 3.772588),
                              ])
    def test_calculate(self, equation, t, T, expected):
        obj = EvaporationEq(a=1.0, b=2.0, c=3.0,
                            equation=equation)

        assert np.isclose(obj.calculate(t, T), expected)
