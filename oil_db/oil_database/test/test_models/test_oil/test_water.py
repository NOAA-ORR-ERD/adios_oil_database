'''
    Test our main Water model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Water


class TestWater():
    @pytest.mark.parametrize('fraction',
                             [
                              {'value': 0.1, 'unit': '1'},
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, fraction):
        if fraction is None:
            obj = Water()
        else:
            obj = Water(fraction=fraction)

        assert obj.fraction.value == float(fraction['value'])
        assert obj.fraction.unit == str(fraction['unit'])

    def test_init_defaults(self):
        # everything has a default
        obj = Water(fraction={'value': 0.1, 'unit': '1'})

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
        obj = Water(fraction={'value': 0.1, 'unit': '1'},
                    weathering=weathering,
                    replicates=replicates,
                    standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
