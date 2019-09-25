'''
    Test our Environment Canada Pour Point model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECPourPoint


class TestECPourPoint():
    def test_init_defaults(self):
        # basically everything has a default
        obj = ECPourPoint()

        assert obj.ref_temp is None
        assert obj.weathering == 0.0

        assert obj.standard_deviation is None
        assert obj.replicates is None
        assert obj.method is None

    @pytest.mark.parametrize('ref_temp, weathering, method',
                             [
                              ({'value': 15.0, 'unit': 'C'},
                               0.1, 'Method'),
                              ({'value': 15.0, 'unit': 'C'},
                               '0.1', 0xdeadbeef),
                              pytest.param(
                                  {'value': 15.0, 'unit': 'C'},
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 15.0, 'unit': 'C'},
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, ref_temp, weathering, method):
        obj = ECPourPoint(ref_temp=ref_temp,
                          weathering=weathering,
                          method=method)

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])
        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
