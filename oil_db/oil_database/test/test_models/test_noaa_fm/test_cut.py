'''
    Test our NOAA Filemaker Distillation cut model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import NoaaFmCut


class TestNoaaFmCut():
    @pytest.mark.parametrize('fraction',
                             [
                              pytest.param(
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              0.1,
                              '0.1',
                              ])
    def test_init_required(self, fraction):
        if fraction is None:
            obj = NoaaFmCut()
        else:
            obj = NoaaFmCut(fraction=fraction)

        assert obj.fraction == float(fraction)

    def test_init_defaults(self):
        obj = NoaaFmCut(fraction=0.1)

        assert obj.vapor_temp_k is None
        assert obj.liquid_temp_k is None
        assert obj.weathering == 0.0

    @pytest.mark.parametrize('vapor_temp, liquid_temp, weathering',
                             [
                              (288.15, 288.15, 0.1),
                              ('288.15', '288.15', '0.1'),
                              pytest.param(
                                  'nope', 288.15, 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  288.15, 288.15, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, vapor_temp, liquid_temp, weathering):
        sara_obj = NoaaFmCut(fraction=1000.0,
                             vapor_temp_k=vapor_temp,
                             liquid_temp_k=liquid_temp,
                             weathering=weathering)

        assert sara_obj.vapor_temp_k == float(vapor_temp)
        assert sara_obj.liquid_temp_k == float(liquid_temp)
        assert sara_obj.weathering == float(weathering)
