'''
    Test our NOAA Filemaker kinematic viscosity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import NoaaFmKVis


class TestNoaaFmKVis():
    @pytest.mark.parametrize('m_2_s, ref_temp',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 273.15,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  1000.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              (1000.0, 273.15),
                              ('1000.0', '273.15'),
                              ])
    def test_init_required(self, m_2_s, ref_temp):
        if m_2_s is None and ref_temp is None:
            obj = NoaaFmKVis()
        elif m_2_s is None:
            obj = NoaaFmKVis(ref_temp_k=ref_temp)
        elif ref_temp is None:
            obj = NoaaFmKVis(m_2_s=m_2_s)
        else:
            obj = NoaaFmKVis(m_2_s=m_2_s, ref_temp_k=ref_temp)

        assert obj.m_2_s == float(m_2_s)
        assert obj.ref_temp_k == float(ref_temp)

    def test_init_defaults(self):
        obj = NoaaFmKVis(m_2_s=1000.0, ref_temp_k=273.15)

        assert obj.weathering == 0.0

    @pytest.mark.parametrize('weathering',
                             [
                              0.1,
                              '0.1',
                              pytest.param(
                                  'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering):
        obj = NoaaFmKVis(m_2_s=1000.0, ref_temp_k=273.15,
                         weathering=weathering)

        assert obj.weathering == float(weathering)
