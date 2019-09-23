'''
    Test our NOAA Filemaker dynamic viscosity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import NoaaFmDVis


class TestNoaaFmDVis():
    @pytest.mark.parametrize('kg_ms, ref_temp',
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
    def test_init_required(self, kg_ms, ref_temp):
        if kg_ms is None and ref_temp is None:
            obj = NoaaFmDVis()
        elif kg_ms is None:
            obj = NoaaFmDVis(ref_temp_k=ref_temp)
        elif ref_temp is None:
            obj = NoaaFmDVis(kg_ms=kg_ms)
        else:
            obj = NoaaFmDVis(kg_ms=kg_ms, ref_temp_k=ref_temp)

        assert obj.kg_ms == float(kg_ms)
        assert obj.ref_temp_k == float(ref_temp)

    def test_init_defaults(self):
        obj = NoaaFmDVis(kg_ms=1000.0, ref_temp_k=273.15)

        assert obj.weathering == 0.0
        assert obj.replicates is None
        assert obj.standard_deviation is None
        assert obj.method is None

    @pytest.mark.parametrize('weathering, replicates, std_dev, method',
                             [
                              (0.1, 3, 0.1, 'method'),
                              ('0.1', '3', '0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 3, 0.1, 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'nope', 0.1, 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3, 'nope', 'method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 3, 0.1, 'ThisMethodNameIsTooLong',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, replicates, std_dev, method):
        obj = NoaaFmDVis(kg_ms=1000.0, ref_temp_k=273.15,
                         weathering=weathering,
                         replicates=replicates,
                         standard_deviation=std_dev,
                         method=method)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
        assert obj.method == str(method)
