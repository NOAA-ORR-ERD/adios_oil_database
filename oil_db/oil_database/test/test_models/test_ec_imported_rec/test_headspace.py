'''
    Test our Environment Canada Headspace model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECHeadspace


class TestECHeadspace():
    def test_init_defaults(self):
        # basically everything has a default
        obj = ECHeadspace()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.n_c5_mg_g is None
        assert obj.n_c6_mg_g is None
        assert obj.n_c7_mg_g is None
        assert obj.n_c8_mg_g is None

        assert obj.c5_group_mg_g is None
        assert obj.c6_group_mg_g is None
        assert obj.c7_group_mg_g is None

    @pytest.mark.parametrize('weathering, method',
                             [
                              (0.1, 'Method'),
                              ('0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method):
        obj = ECHeadspace(weathering=weathering,
                          method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
