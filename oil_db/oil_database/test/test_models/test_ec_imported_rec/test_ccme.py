'''
    Test our Environment Canada CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import EcCCMEFraction


class TestEcCCMEFraction():
    def test_init_defaults(self):
        obj = EcCCMEFraction()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.f1_mg_g is None
        assert obj.f2_mg_g is None
        assert obj.f3_mg_g is None
        assert obj.f4_mg_g is None

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
        obj = EcCCMEFraction(weathering=weathering,
                             method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
