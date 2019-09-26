'''
    Test our main Interfacial Tension model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import InterfacialTension


class TestInterfacialTension():
    @pytest.mark.parametrize('tension, ref_temp, interface',
                             [
                              ({'value': 10.0, 'unit': 'dyne/cm'},
                               {'value': 15.0, 'unit': 'C'},
                               'water'),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'}, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, {'value': 15.0, 'unit': 'C'}, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': 'dyne/cm'},
                                  None,
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': 'dyne/cm'},
                                  None,
                                  'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope',
                                  {'value': 15.0, 'unit': 'C'},
                                  'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': 'dyne/cm'},
                                  'nope',
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  {'value': 10.0, 'unit': 'dyne/cm'},
                                  {'value': 15.0, 'unit': 'C'},
                                  'NotAnEnum',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, tension, ref_temp, interface):
        if tension is None and ref_temp is None and interface is None:
            obj = InterfacialTension()
        elif ref_temp is None and interface is None:
            obj = InterfacialTension(tension=tension)
        elif tension is None and interface is None:
            obj = InterfacialTension(ref_temp=ref_temp)
        elif tension is None and ref_temp is None:
            obj = InterfacialTension(interface=interface)
        elif tension is None:
            obj = InterfacialTension(ref_temp=ref_temp,
                                     interface=interface)
        elif ref_temp is None:
            obj = InterfacialTension(tension=tension,
                                     interface=interface)
        elif interface is None:
            obj = InterfacialTension(tension=tension,
                                     ref_temp=ref_temp)
        else:
            obj = InterfacialTension(tension=tension,
                                     ref_temp=ref_temp,
                                     interface=interface)

        assert obj.tension.value == float(tension['value'])
        assert obj.tension.unit == str(tension['unit'])

        assert obj.ref_temp.value == float(ref_temp['value'])
        assert obj.ref_temp.unit == str(ref_temp['unit'])

        assert obj.interface == str(interface)

    def test_init_defaults(self):
        obj = InterfacialTension(tension={'value': 10.0, 'unit': 'dyne/cm'},
                                 ref_temp={'value': 15.0, 'unit': 'C'},
                                 interface='water')

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
        obj = InterfacialTension(tension={'value': 10.0, 'unit': 'dyne/cm'},
                                 ref_temp={'value': 15.0, 'unit': 'C'},
                                 interface='water',
                                 weathering=weathering,
                                 method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
