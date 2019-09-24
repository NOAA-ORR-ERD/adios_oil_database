'''
    Test our Environment Canada CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECCorexit9500


class TestECCorexit9500():
    def test_init_defaults(self):
        obj = ECCorexit9500()

        assert obj.weathering == 0.0

        assert obj.dispersant_effectiveness is None
        assert obj.standard_deviation is None
        assert obj.replicates is None

    @pytest.mark.parametrize('weathering',
                             [
                              0.1,
                              '0.1',
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering):
        obj = ECCorexit9500(weathering=weathering)

        assert obj.weathering == float(weathering)

    def test_init_effectiveness(self):
        effectiveness = {'value': 10.0, 'unit': '%'}
        obj = ECCorexit9500(dispersant_effectiveness=effectiveness)

        assert obj.dispersant_effectiveness.value == effectiveness['value']
        assert obj.dispersant_effectiveness.unit == effectiveness['unit']
