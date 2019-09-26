'''
    Test our main Headspace model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Headspace


class TestHeadspace():
    def test_init_defaults(self):
        # basically everything has a default
        obj = Headspace()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.n_c5 is None
        assert obj.n_c6 is None
        assert obj.n_c7 is None
        assert obj.n_c8 is None

        assert obj.c5_group is None
        assert obj.c6_group is None
        assert obj.c7_group is None

    @pytest.mark.parametrize('weathering, method, n_c5',
                             [
                              (0.1, 'Method', {'value': 10, 'unit': 'ug/g'}),
                              ('0.1', 0xdeadbeef, {'value': 10,
                                                     'unit': 'ug/g'}),
                              pytest.param(
                                  'nope', 'Method', {'value': 10,
                                                     'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  {'value': 10, 'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, n_c5):
        obj = Headspace(weathering=weathering, method=method, n_c5=n_c5)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.n_c5.value == float(n_c5['value'])
        assert obj.n_c5.unit == str(n_c5['unit'])
