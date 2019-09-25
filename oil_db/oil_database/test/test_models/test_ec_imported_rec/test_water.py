'''
    Test our Environment Canada Water model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECWater


class TestECWater():
    def test_init_defaults(self):
        # everything has a default
        obj = ECWater()

        assert obj.percent is None
        assert obj.weathering == 0.0

        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('percent, weathering',
                             [
                              ({'value': 10.0, 'unit': '%'}, 0.1),
                              ({'value': 10.0, 'unit': '%'}, '0.1'),
                              pytest.param(
                                  {'value': 10.0, 'unit': '%'}, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, percent, weathering):
        obj = ECWater(percent=percent, weathering=weathering)

        assert obj.percent.value == percent['value']
        assert obj.percent.unit == percent['unit']

        assert obj.weathering == float(weathering)
