'''
    Test our main Density model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Density


class TestDensity():
    @pytest.mark.parametrize('density, ref_temp',
                             [
                              ({'value': 100.0, 'unit': 'g/mL'},
                               {'value': 15.0, 'unit': 'C'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'g/mL'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', {'value': 15.0, 'unit': 'C'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 100.0, 'unit': 'g/mL'}, 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, density, ref_temp):
        if density is None and ref_temp is None:
            obj = Density()
        elif ref_temp is None:
            obj = Density(density=density)
        elif density is None:
            obj = Density(ref_temp=ref_temp)
        else:
            obj = Density(density=density, ref_temp=ref_temp)

        assert obj.density.value == float(density['value'])
        assert obj.density.unit == str(density['unit'])

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])

    def test_init_defaults(self):
        obj = Density(density={'value': 100.0, 'unit': 'g/mL'},
                      ref_temp={'value': 15.0, 'unit': 'C'})

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
        obj = Density(density={'value': 100.0, 'unit': 'g/mL'},
                      ref_temp={'value': 15.0, 'unit': 'C'},
                      weathering=weathering,
                      replicates=replicates,
                      standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
