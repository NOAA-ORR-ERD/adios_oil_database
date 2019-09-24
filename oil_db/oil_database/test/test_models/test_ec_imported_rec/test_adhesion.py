'''
    Test our Environment Canada Adhesion model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECAdhesion


class TestECAdhesion():
    @pytest.mark.parametrize('g_cm_2',
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
    def test_init_required(self, g_cm_2):
        if g_cm_2 is None:
            obj = ECAdhesion()
        else:
            obj = ECAdhesion(g_cm_2=g_cm_2)

        assert obj.g_cm_2 == float(g_cm_2)

    def test_init_defaults(self):
        obj = ECAdhesion(g_cm_2=10.0)

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
        obj = ECAdhesion(g_cm_2=10.0,
                         weathering=weathering,
                         replicates=replicates,
                         standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
