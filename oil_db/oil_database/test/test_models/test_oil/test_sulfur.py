'''
    Test our main Sulfur model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Sulfur


class TestSulfur():
    @pytest.mark.parametrize('fraction',
                             [
                              {'value': 10.0, 'unit': '%'},
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, fraction):
        if fraction is None:
            obj = Sulfur()
        else:
            obj = Sulfur(fraction=fraction)

        assert obj.fraction.value == float(fraction['value'])
        assert obj.fraction.unit == str(fraction['unit'])

    def test_init_defaults(self):
        obj = Sulfur(fraction={'value': 10.0, 'unit': '%'})

        assert obj.weathering == 0.0

        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, replicates, std_dev',
                             [
                              (0.1, 3.0, 0.2),
                              ('0.1', '3.0', '0.2'),
                              pytest.param(
                                  'nope', 3.0, 0.2,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'nope', 0.2,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, replicates, std_dev):
        obj = Sulfur(fraction={'value': 10.0, 'unit': '%'},
                     weathering=weathering,
                     replicates=replicates,
                     standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
