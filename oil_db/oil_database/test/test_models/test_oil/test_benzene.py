'''
    Test our main Benzene model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Benzene


class TestBenzene():
    def test_init_defaults(self):
        obj = Benzene()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.benzene is None
        assert obj.toluene is None
        assert obj.ethylbenzene is None
        assert obj.m_p_xylene is None
        assert obj.o_xylene is None

        assert obj.isopropylbenzene is None
        assert obj.propylebenzene is None
        assert obj.isobutylbenzene is None
        assert obj.amylbenzene is None
        assert obj.n_hexylbenzene is None

        assert obj.x1_2_3_trimethylbenzene is None
        assert obj.x1_2_4_trimethylbenzene is None
        assert obj.x1_2_dimethyl_4_ethylbenzene is None
        assert obj.x1_3_5_trimethylbenzene is None
        assert obj.x1_methyl_2_isopropylbenzene is None
        assert obj.x2_ethyltoluene is None
        assert obj.x3_4_ethyltoluene is None

    @pytest.mark.parametrize('weathering, method, x2_ethyltoluene',
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
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, x2_ethyltoluene):
        obj = Benzene(weathering=weathering,
                      method=method,
                      x2_ethyltoluene=x2_ethyltoluene)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.x2_ethyltoluene.value == float(x2_ethyltoluene['value'])
        assert obj.x2_ethyltoluene.unit == str(x2_ethyltoluene['unit'])
