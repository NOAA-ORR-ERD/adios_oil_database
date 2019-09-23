'''
    Test our NOAA Filemaker density model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import NoaaFmDensity


class TestNoaaFmDensity():
    @pytest.mark.parametrize('kg_m_3, ref_temp',
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
    def test_init_required(self, kg_m_3, ref_temp):
        if kg_m_3 is None and ref_temp is None:
            obj = NoaaFmDensity()
        elif kg_m_3 is None:
            obj = NoaaFmDensity(ref_temp_k=ref_temp)
        elif ref_temp is None:
            obj = NoaaFmDensity(kg_m_3=kg_m_3)
        else:
            obj = NoaaFmDensity(kg_m_3=kg_m_3, ref_temp_k=ref_temp)

        assert obj.kg_m_3 == float(kg_m_3)
        assert obj.ref_temp_k == float(ref_temp)

    def test_init_defaults(self):
        obj = NoaaFmDensity(kg_m_3=1000.0, ref_temp_k=273.15)

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
        obj = NoaaFmDensity(kg_m_3=1000.0, ref_temp_k=273.15,
                            weathering=weathering,
                            replicates=replicates,
                            standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
