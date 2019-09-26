'''
    Test our main Evaporation Equation model class
'''
import numpy as np

import pytest

from pydantic import ValidationError

from oil_database.models.oil import EvaporationEq


class TestEvaporationEq():
    @pytest.mark.parametrize('a, b, c, equation',
                             [
                              (1.0, 2.0, 3.0, '(A + BT) ln t'),
                              ('1.0', '2.0', '3.0', '(A + BT) ln t'),
                              pytest.param(
                                  None, None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 3.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 3.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, 3.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 2.0, 3.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, 3.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, None, 3.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, None, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, 3.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope', 2.0, 3.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 'nope', 3.0, '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, 'nope', '(A + BT) ln t',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1.0, 2.0, 3.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, a, b, c, equation):
        if a is None and b is None and c is None and equation is None:
            obj = EvaporationEq()
        elif b is None and c is None and equation is None:
            obj = EvaporationEq(a=a)
        elif a is None and c is None and equation is None:
            obj = EvaporationEq(b=b)
        elif a is None and b is None and equation is None:
            obj = EvaporationEq(c=c)
        elif a is None and b is None and c is None:
            obj = EvaporationEq(equation=equation)
        elif c is None and equation is None:
            obj = EvaporationEq(a=a, b=b)
        elif b is None and equation is None:
            obj = EvaporationEq(a=a, c=c)
        elif b is None and c is None:
            obj = EvaporationEq(a=a, equation=equation)
        elif a is None and equation is None:
            obj = EvaporationEq(b=b, c=c)
        elif a is None and c is None:
            obj = EvaporationEq(b=b, equation=equation)
        elif a is None and b is None:
            obj = EvaporationEq(c=c, equation=equation)
        elif equation is None:
            obj = EvaporationEq(a=a, b=b, c=c)
        elif c is None:
            obj = EvaporationEq(a=a, b=b, equation=equation)
        elif b is None:
            obj = EvaporationEq(a=a, c=c, equation=equation)
        elif a is None:
            obj = EvaporationEq(b=b, c=c, equation=equation)
        else:
            obj = EvaporationEq(a=a, b=b, c=c, equation=equation)

        assert obj.a == float(a)
        assert obj.b == float(b)
        assert obj.c == float(c)
        assert obj.equation == str(equation)

    def test_init_defaults(self):
        obj = EvaporationEq(a=1.0, b=2.0, c=3.0, equation='(A + BT) ln t')

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
        obj = EvaporationEq(a=1.0, b=2.0, c=3.0, equation='(A + BT) ln t',
                            weathering=weathering)

        assert obj.weathering == float(weathering)

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
