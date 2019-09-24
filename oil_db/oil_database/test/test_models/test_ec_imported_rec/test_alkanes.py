'''
    Test our Environment Canada Alkanes model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECNAlkanes


class TestECNAlkanes():
    def test_init_defaults(self):
        # basically everything has a default
        obj = ECNAlkanes()

        assert obj.weathering == 0.0
        assert obj.method is None
        assert obj.pristane_ug_g is None
        assert obj.phytane_ug_g is None
        assert obj.c8_ug_g is None
        assert obj.c9_ug_g is None
        assert obj.c10_ug_g is None
        assert obj.c11_ug_g is None
        assert obj.c12_ug_g is None
        assert obj.c13_ug_g is None
        assert obj.c14_ug_g is None
        assert obj.c15_ug_g is None
        assert obj.c16_ug_g is None
        assert obj.c17_ug_g is None
        assert obj.c18_ug_g is None
        assert obj.c19_ug_g is None
        assert obj.c20_ug_g is None
        assert obj.c21_ug_g is None
        assert obj.c22_ug_g is None
        assert obj.c23_ug_g is None
        assert obj.c24_ug_g is None
        assert obj.c25_ug_g is None
        assert obj.c26_ug_g is None
        assert obj.c27_ug_g is None
        assert obj.c28_ug_g is None
        assert obj.c29_ug_g is None
        assert obj.c30_ug_g is None
        assert obj.c31_ug_g is None
        assert obj.c32_ug_g is None
        assert obj.c33_ug_g is None
        assert obj.c34_ug_g is None
        assert obj.c35_ug_g is None
        assert obj.c36_ug_g is None
        assert obj.c37_ug_g is None
        assert obj.c38_ug_g is None
        assert obj.c39_ug_g is None
        assert obj.c40_ug_g is None
        assert obj.c41_ug_g is None
        assert obj.c42_ug_g is None
        assert obj.c43_ug_g is None
        assert obj.c44_ug_g is None

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
        # we will not test every attribute, just the ones that have
        # constraints
        obj = ECNAlkanes(weathering=weathering,
                         method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
