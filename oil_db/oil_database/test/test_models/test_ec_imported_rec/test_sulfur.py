'''
    Test our Environment Canada Sulfur model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECSulfur


class TestECSulfur():
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
            obj = ECSulfur()
        else:
            obj = ECSulfur(percent=percent)

        assert obj.percent == float(percent)

    def test_init_defaults(self):
        obj = ECSulfur(percent=10.0)

        assert obj.weathering == 0.0

        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering',
                             [
                              0.1,
                              '0.1',
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering):
        obj = ECSulfur(percent=10.0, weathering=weathering)

        assert obj.weathering == float(weathering)
