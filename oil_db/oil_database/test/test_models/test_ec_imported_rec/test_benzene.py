'''
    Test our Environment Canada Benzene model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECBenzene


class TestECBenzene():
    def test_init_defaults(self):
        obj = ECBenzene()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.benzene_ug_g is None
        assert obj.toluene_ug_g is None
        assert obj.ethylbenzene_ug_g is None
        assert obj.m_p_xylene_ug_g is None
        assert obj.o_xylene_ug_g is None

        assert obj.isopropylbenzene_ug_g is None
        assert obj.propylebenzene_ug_g is None
        assert obj.isobutylbenzene_ug_g is None
        assert obj.amylbenzene_ug_g is None
        assert obj.n_hexylbenzene_ug_g is None

        assert obj.x1_2_3_trimethylbenzene_ug_g is None
        assert obj.x1_2_4_trimethylbenzene_ug_g is None
        assert obj.x1_2_dimethyl_4_ethylbenzene_ug_g is None
        assert obj.x1_3_5_trimethylbenzene_ug_g is None
        assert obj.x1_methyl_2_isopropylbenzene_ug_g is None
        assert obj.x2_ethyltoluene_ug_g is None
        assert obj.x3_4_ethyltoluene_ug_g is None

    @pytest.mark.parametrize('weathering, method, x2_ethyltoluene_ug_g',
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
    def test_init_optional(self, weathering, method, x2_ethyltoluene_ug_g):
        obj = ECBenzene(weathering=weathering,
                        method=method,
                        x2_ethyltoluene_ug_g=x2_ethyltoluene_ug_g)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.x2_ethyltoluene_ug_g == float(x2_ethyltoluene_ug_g)
