'''
    Test our main Conradson model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Conradson


class TestConradson():
    def test_init_defaults(self):
        obj = Conradson()

        assert obj.weathering == 0.0

        assert obj.residue is None
        assert obj.crude is None

    @pytest.mark.parametrize('weathering, residue, crude',
                             [
                              (0.1,
                               {'value': 5.0, 'unit': '%'},
                               {'value': 10.0, 'unit': '%'}),
                              ('0.1',
                               {'value': 5.0, 'unit': '%'},
                               {'value': 10.0, 'unit': '%'}),
                              pytest.param(
                                  'nope',
                                  {'value': 5.0, 'unit': '%'},
                                  {'value': 10.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'nope',
                                  {'value': 10.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  {'value': 10.0, 'unit': '%'},
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, residue, crude):
        obj = Conradson(weathering=weathering, residue=residue, crude=crude)

        assert obj.weathering == float(weathering)

        assert obj.residue.value == float(residue['value'])
        assert obj.residue.unit == str(residue['unit'])

        assert obj.crude.value == float(crude['value'])
        assert obj.crude.unit == str(crude['unit'])
