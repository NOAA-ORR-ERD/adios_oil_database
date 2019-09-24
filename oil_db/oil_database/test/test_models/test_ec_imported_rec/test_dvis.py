'''
    Test our Environment Canada Dynamic Viscosity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECDVis


class TestECDVis():
    @pytest.mark.parametrize('mpa_s, ref_temp_c',
                             [
                              ({'value': 100.0, 'unit': 'mPa s'}, 15.0),
                              ({'value': 100.0, 'unit': 'mPa s'}, '15.0'),
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
    def test_init_required(self, mpa_s, ref_temp_c):
        if mpa_s is None and ref_temp_c is None:
            obj = ECDVis()
        elif ref_temp_c is None:
            obj = ECDVis(mpa_s=mpa_s)
        elif mpa_s is None:
            obj = ECDVis(ref_temp_c=ref_temp_c)
        else:
            obj = ECDVis(mpa_s=mpa_s, ref_temp_c=ref_temp_c)

        assert obj.mpa_s.value == float(mpa_s['value'])
        assert obj.mpa_s.unit == str(mpa_s['unit'])

        assert obj.ref_temp_c == float(ref_temp_c)

    def test_init_defaults(self):
        obj = ECDVis(mpa_s={'value': 100.0, 'unit': 'mPa s'}, ref_temp_c=15.0)

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
        obj = ECDVis(mpa_s={'value': 100.0, 'unit': 'mPa s'}, ref_temp_c=15.0,
                     weathering=weathering,
                     replicates=replicates,
                     standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
