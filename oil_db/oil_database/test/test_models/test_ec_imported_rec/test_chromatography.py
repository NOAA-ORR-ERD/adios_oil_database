'''
    Test our Environment Canada CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECGasChromatography


class TestECGasChromatography():
    def test_init_defaults(self):
        obj = ECGasChromatography()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.tph_mg_g is None
        assert obj.tsh_mg_g is None
        assert obj.tah_mg_g is None

        assert obj.tsh_tph_percent is None
        assert obj.tah_tph_percent is None
        assert obj.resolved_peaks_tph_percent is None

    @pytest.mark.parametrize('weathering, method',
                             [
                              (0.1, 'Method'),
                              ('0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method):
        obj = ECGasChromatography(weathering=weathering,
                                  method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
