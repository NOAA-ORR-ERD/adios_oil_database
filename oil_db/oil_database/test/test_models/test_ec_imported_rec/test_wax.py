'''
    Test our Environment Canada Wax model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECWax


class TestECWax():
    @pytest.mark.parametrize('percent',
                             [
                              10.0,
                              '10.0',
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, percent):
        if percent is None:
            obj = ECWax()
        else:
            obj = ECWax(percent=percent)

        assert obj.percent == float(percent)

    def test_init_defaults(self):
        # everything has a default
        obj = ECWax(percent=10.0)

        assert obj.weathering == 0.0

        assert obj.method is None
        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, method',
                             [
                              (0.1, 'Method'),
                              ('0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, '123456789 1234567',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method):
        obj = ECWax(percent=10.0, weathering=weathering, method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
