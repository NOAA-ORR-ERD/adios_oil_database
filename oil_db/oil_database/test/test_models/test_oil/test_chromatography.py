'''
    Test our main CCME Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import GasChromatography


class TestGasChromatography():
    def test_init_defaults(self):
        obj = GasChromatography()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.tph is None
        assert obj.tsh is None
        assert obj.tah is None

        assert obj.tsh_tph is None
        assert obj.tah_tph is None
        assert obj.resolved_peaks_tph is None

    @pytest.mark.parametrize('weathering, method, tph',
                             [
                              (0.1, 'Method', {'value': 10.0, 'unit': 'mg/g'}),
                              ('0.1', 0xdeadbeef, {'value': 10.0,
                                                   'unit': 'mg/g'}),
                              pytest.param(
                                  'nope', 'Method', {'value': 10.0,
                                                     'unit': 'mg/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'MethodNameTooLong', {'value': 10.0,
                                                             'unit': 'mg/g'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, tph):
        obj = GasChromatography(weathering=weathering,
                                method=method, tph=tph)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.tph.value == float(tph['value'])
        assert obj.tph.unit == str(tph['unit'])
