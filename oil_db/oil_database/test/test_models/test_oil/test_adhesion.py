'''
    Test our Environment Canada Adhesion model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Adhesion


class TestAdhesion():
    @pytest.mark.parametrize('adhesion',
                             [
                              {'value': 10.0, 'unit': 'g/cm^2'},
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, adhesion):
        if adhesion is None:
            obj = Adhesion()
        else:
            obj = Adhesion(adhesion=adhesion)

        assert obj.adhesion.value == float(adhesion['value'])
        assert obj.adhesion.unit == str(adhesion['unit'])

    def test_init_defaults(self):
        obj = Adhesion(adhesion={'value': 10.0, 'unit': 'g/cm^2'})

        assert obj.weathering == 0.0
        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, replicates, std_dev',
                             [
                              (0.1, 3, 0.1),
                              ('0.1', '3', '0.1'),
                              pytest.param(
                                  'nope', 3, 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, replicates, std_dev):
        obj = Adhesion(adhesion={'value': 10.0, 'unit': 'g/cm^2'},
                       weathering=weathering,
                       replicates=replicates,
                       standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
