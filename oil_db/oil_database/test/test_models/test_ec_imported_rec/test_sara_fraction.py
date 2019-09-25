'''
    Test our Environment Canada SARA Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECSARAFraction


class TestECSARAFraction():
    @pytest.mark.parametrize('sara_type, percent',
                             [
                              ('Aromatics', 10.0),
                              ('Aromatics', '10.0'),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Aromatics', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'NotAnEnum', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Aromatics', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, sara_type, percent):
        if sara_type is None and percent is None:
            obj = ECSARAFraction()
        elif percent is None:
            obj = ECSARAFraction(sara_type=sara_type)
        elif sara_type is None:
            obj = ECSARAFraction(percent=percent)
        else:
            obj = ECSARAFraction(sara_type=sara_type, percent=percent)

        assert obj.sara_type == str(sara_type)
        assert obj.percent == float(percent)

    def test_init_defaults(self):
        obj = ECSARAFraction(sara_type='Aromatics', percent=10.0)

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, method',
                             [
                              (0.1, 'Method'),
                              ('0.1', 0xdeadbeef),
                              pytest.param(
                                  'nope', 'Method',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method):
        obj = ECSARAFraction(sara_type='Aromatics', percent=10.0,
                             weathering=weathering,
                             method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
