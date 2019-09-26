'''
    Test our main SARA Fraction model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import SARAFraction
from mpmath import fraction


class TestSARAFraction():
    @pytest.mark.parametrize('sara_type, fraction',
                             [
                              ('Aromatics', {'value': 10.0, 'unit': '%'}),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Aromatics', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 10.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'NotAnEnum', {'value': 10.0, 'unit': '%'},
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Aromatics', 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, sara_type, fraction):
        if sara_type is None and fraction is None:
            obj = SARAFraction()
        elif fraction is None:
            obj = SARAFraction(sara_type=sara_type)
        elif sara_type is None:
            obj = SARAFraction(fraction=fraction)
        else:
            obj = SARAFraction(sara_type=sara_type, fraction=fraction)

        assert obj.sara_type == str(sara_type)

        assert obj.fraction.value == float(fraction['value'])
        assert obj.fraction.unit == str(fraction['unit'])

    def test_init_defaults(self):
        obj = SARAFraction(sara_type='Aromatics',
                           fraction={'value': 10.0, 'unit': '%'})

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.replicates is None
        assert obj.standard_deviation is None

    @pytest.mark.parametrize('weathering, method, replicates, std_dev',
                             [
                              (0.1, 'Method', 3.0, 0.2),
                              ('0.1', 0xdeadbeef, '3.0', '0.2'),
                              pytest.param(
                                  'nope', 'Method', 3.0, 0.2,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1,
                                  'LongMethod 123456789 123456789 123456789 ',
                                  3.0, 0.2,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 'nope', 0.2,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.1, 'Method', 3.0, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, replicates, std_dev):
        obj = SARAFraction(sara_type='Aromatics',
                           fraction={'value': 10.0, 'unit': '%'},
                           weathering=weathering,
                           method=method,
                           replicates=replicates,
                           standard_deviation=std_dev)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.replicates == float(replicates)
        assert obj.standard_deviation == float(std_dev)
