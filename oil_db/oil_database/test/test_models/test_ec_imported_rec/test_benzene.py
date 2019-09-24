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

        assert obj._1_2_3_trimethylbenzene_ug_g is None
        assert obj._1_2_4_trimethylbenzene_ug_g is None
        assert obj._1_2_dimethyl_4_ethylbenzene_ug_g is None
        assert obj._1_3_5_trimethylbenzene_ug_g is None
        assert obj._1_methyl_2_isopropylbenzene_ug_g is None
        assert obj._2_ethyltoluene_ug_g is None
        assert obj._3_4_ethyltoluene_ug_g is None

    @pytest.mark.parametrize('weathering, method',
                             [
                              (0.1, 'Method'),
                              ('0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method):
        obj = ECBenzene(weathering=weathering,
                        method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
