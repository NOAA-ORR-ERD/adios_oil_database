'''
    Test our main Biomarkers model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import Biomarkers


class TestBiomarkers():
    def test_init_defaults(self):
        obj = Biomarkers()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.c21_tricyclic_terpane is None
        assert obj.c22_tricyclic_terpane is None
        assert obj.c23_tricyclic_terpane is None
        assert obj.c24_tricyclic_terpane is None

        assert obj.x30_norhopane is None
        assert obj.hopane is None
        assert obj.x30_homohopane_22s is None
        assert obj.x30_homohopane_22r is None

        assert obj.x30_31_bishomohopane_22s is None
        assert obj.x30_31_bishomohopane_22r is None

        assert obj.x30_31_trishomohopane_22s is None
        assert obj.x30_31_trishomohopane_22r is None

        assert obj.tetrakishomohopane_22s is None
        assert obj.tetrakishomohopane_22r is None

        assert obj.pentakishomohopane_22s is None
        assert obj.pentakishomohopane_22r is None

        assert obj.x18a_22_29_30_trisnorneohopane is None
        assert obj.x17a_h_22_29_30_trisnorhopane is None

        assert obj.x14b_h_17b_h_20_cholestane is None
        assert obj.x14b_h_17b_h_20_methylcholestane is None
        assert obj.x14b_h_17b_h_20_ethylcholestane is None

    @pytest.mark.parametrize('weathering, method, x30_norhopane',
                             [
                              (0.1, 'Method', {'value': 10.0, 'unit': 'ug/g'}),
                              ('0.1', 0xdeadbeef, {'value': 10.0,
                                                   'unit': 'ug/g'}),
                              pytest.param(
                                  'nope', 'Method', {'value': 10.0,
                                                     'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', {'value': 10.0,
                                                             'unit': 'ug/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, x30_norhopane):
        obj = Biomarkers(weathering=weathering,
                         method=method,
                         x30_norhopane=x30_norhopane)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.x30_norhopane.value == float(x30_norhopane['value'])
        assert obj.x30_norhopane.unit == str(x30_norhopane['unit'])
