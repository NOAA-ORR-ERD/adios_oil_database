'''
    Test our Environment Canada CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECCut


class TestECCut():
    @pytest.mark.parametrize('percent',
                             [
                              10.0,
                              '10.0',
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, percent):
        if percent is None:
            obj = ECCut()
        else:
            obj = ECCut(percent=percent)

        assert obj.percent == float(percent)

    def test_init_defaults(self):
        obj = ECCut(percent=10.0)

        assert obj.temp_c is None
        assert obj.weathering == 0.0
        assert obj.method is None

    @pytest.mark.parametrize('temp_c, weathering, method',
                             [
                              (273.15, 0.1, 'Method'),
                              ('273.15', '0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 0.1, 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  273.15, 'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  273.15, 0.1,
                                  'LongMethod'
                                  '123456789 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, temp_c, weathering, method):
        obj = ECCut(percent=10.0,
                    temp_c=temp_c,
                    weathering=weathering,
                    method=method)

        assert obj.temp_c == float(temp_c)
        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
