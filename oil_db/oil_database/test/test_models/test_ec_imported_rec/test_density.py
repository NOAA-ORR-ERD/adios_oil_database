'''
    Test our Environment Canada Density model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECDensity


class TestECDensity():
    @pytest.mark.parametrize('g_ml, ref_temp_c',
                             [
                              (100.0, 15.0),
                              ('100.0', '15.0'),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 15.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  100.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 15.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  100.0, 'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, g_ml, ref_temp_c):
        if g_ml is None and ref_temp_c is None:
            obj = ECDensity()
        elif ref_temp_c is None:
            obj = ECDensity(g_ml=g_ml)
        elif g_ml is None:
            obj = ECDensity(ref_temp_c=ref_temp_c)
        else:
            obj = ECDensity(g_ml=g_ml, ref_temp_c=ref_temp_c)

        assert obj.g_ml == float(g_ml)
        assert obj.ref_temp_c == float(ref_temp_c)

    def test_init_defaults(self):
        obj = ECDensity(g_ml=100.0, ref_temp_c=15.0)

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
        obj = ECDensity(g_ml=100.0, ref_temp_c=273.15,
                        weathering=weathering,
                        replicates=replicates,
                        standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
