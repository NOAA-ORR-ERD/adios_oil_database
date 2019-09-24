'''
    Test our Environment Canada Biomarkers model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECBiomarkers


class TestECBiomarkers():
    def test_init_defaults(self):
        obj = ECBiomarkers()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.c21_tricyclic_terpane_ug_g is None
        assert obj.c22_tricyclic_terpane_ug_g is None
        assert obj.c23_tricyclic_terpane_ug_g is None
        assert obj.c24_tricyclic_terpane_ug_g is None

        assert obj._30_norhopane_ug_g is None
        assert obj.hopane_ug_g is None
        assert obj._30_homohopane_22s_ug_g is None
        assert obj._30_homohopane_22r_ug_g is None

        assert obj._30_31_bishomohopane_22s_ug_g is None
        assert obj._30_31_bishomohopane_22r_ug_g is None

        assert obj._30_31_trishomohopane_22s_ug_g is None
        assert obj._30_31_trishomohopane_22r_ug_g is None

        assert obj.tetrakishomohopane_22s_ug_g is None
        assert obj.tetrakishomohopane_22r_ug_g is None

        assert obj.pentakishomohopane_22s_ug_g is None
        assert obj.pentakishomohopane_22r_ug_g is None

        assert obj._18a_22_29_30_trisnorneohopane_ug_g is None
        assert obj._17a_h_22_29_30_trisnorhopane_ug_g is None

        assert obj._14b_h_17b_h_20_cholestane_ug_g is None
        assert obj._14b_h_17b_h_20_methylcholestane_ug_g is None
        assert obj._14b_h_17b_h_20_ethylcholestane_ug_g is None

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
        obj = ECBiomarkers(weathering=weathering,
                           method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
