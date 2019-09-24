'''
    Test our Environment Canada API gravity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECApiGravity


class TestECApiGravity():
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
            obj = ECApiGravity()
        else:
            obj = ECApiGravity(gravity=gravity)

        assert obj.gravity == float(gravity)

    def test_init_defaults(self):
        obj = ECApiGravity(gravity=10.0)

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
        obj = ECApiGravity(gravity=10.0, weathering=weathering)

        assert obj.weathering == float(weathering)
