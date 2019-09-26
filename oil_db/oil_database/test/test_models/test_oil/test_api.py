'''
    Test our main API gravity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import ApiGravity


class TestApiGravity():
    @pytest.mark.parametrize('gravity',
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
    def test_init_required(self, gravity):
        if gravity is None:
            obj = ApiGravity()
        else:
            obj = ApiGravity(gravity=gravity)

        assert obj.gravity == float(gravity)

    def test_init_defaults(self):
        obj = ApiGravity(gravity=10.0)

        assert obj.weathering == 0.0

    @pytest.mark.parametrize('weathering',
                             [
                              0.1,
                              '0.1',
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering):
        obj = ApiGravity(gravity=10.0, weathering=weathering)

        assert obj.weathering == float(weathering)
