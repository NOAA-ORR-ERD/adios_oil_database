'''
    Test our Environment Canada Interfacial Tension model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECInterfacialTension


class TestECInterfacialTension():
    @pytest.mark.parametrize('dynes_cm, ref_temp_c, interface',
                             [
                              (10.0, 15.0, 'water'),
                              ('10.0', '15.0', 'water'),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 15.0, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 15.0, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, None, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'nope', 15.0, 'water',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 'nope', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  10.0, 15.0, 'NotAnEnum',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, dynes_cm, ref_temp_c, interface):
        if dynes_cm is None and ref_temp_c is None and interface is None:
            obj = ECInterfacialTension()
        elif ref_temp_c is None and interface is None:
            obj = ECInterfacialTension(dynes_cm=dynes_cm)
        elif dynes_cm is None and interface is None:
            obj = ECInterfacialTension(ref_temp_c=ref_temp_c)
        elif dynes_cm is None and ref_temp_c is None:
            obj = ECInterfacialTension(interface=interface)
        elif dynes_cm is None:
            obj = ECInterfacialTension(ref_temp_c=ref_temp_c,
                                       interface=interface)
        elif ref_temp_c is None:
            obj = ECInterfacialTension(dynes_cm=dynes_cm,
                                       interface=interface)
        elif interface is None:
            obj = ECInterfacialTension(dynes_cm=dynes_cm,
                                       ref_temp_c=ref_temp_c)
        else:
            obj = ECInterfacialTension(dynes_cm=dynes_cm,
                                       ref_temp_c=ref_temp_c,
                                       interface=interface)

        assert obj.dynes_cm == float(dynes_cm)
        assert obj.ref_temp_c == float(ref_temp_c)
        assert obj.interface == str(interface)

    def test_init_defaults(self):
        obj = ECInterfacialTension(dynes_cm=10.0,
                                   ref_temp_c=15.0,
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
        obj = ECInterfacialTension(dynes_cm=10.0,
                                   ref_temp_c=15.0,
                                   interface='water',
                                   weathering=weathering,
                                   method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
