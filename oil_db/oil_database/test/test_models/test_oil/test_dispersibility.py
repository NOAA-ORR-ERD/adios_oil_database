'''
    Test our main Dispersibility model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import ChemicalDispersibility


class TestChemicalDispersibility():
    @pytest.mark.parametrize('dispersant, effectiveness',
                             [
                              ('Dispersant', {'value': 15.0, 'unit': '%'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Dispersant', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'DispersantNameTooLong',
                                  {'value': 15.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Dispersant', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, dispersant, effectiveness):
        if dispersant is None and effectiveness is None:
            obj = ChemicalDispersibility()
        elif effectiveness is None:
            obj = ChemicalDispersibility(dispersant=dispersant)
        elif dispersant is None:
            obj = ChemicalDispersibility(effectiveness=effectiveness)
        else:
            obj = ChemicalDispersibility(dispersant=dispersant,
                                         effectiveness=effectiveness)

        assert obj.dispersant == str(dispersant)

        assert obj.effectiveness.value == float(effectiveness['value'])
        assert obj.effectiveness.unit == str(effectiveness['unit'])

    def test_init_defaults(self):
        obj = ChemicalDispersibility(dispersant='Dispersant',
                                     effectiveness={'value': 15.0,
                                                    'unit': '%'})

        assert obj.weathering == 0.0
        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, replicates, std_dev',
                             [
                              (0.1, 3, 0.01),
                              ('0.1', '3', '0.01'),
                              pytest.param(
                                  'nope', 3, 0.01,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'nope', 0.01,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, replicates, std_dev):
        obj = ChemicalDispersibility(dispersant='Dispersant',
                                     effectiveness={'value': 15.0,
                                                    'unit': '%'},
                                     weathering=weathering,
                                     replicates=replicates,
                                     standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
