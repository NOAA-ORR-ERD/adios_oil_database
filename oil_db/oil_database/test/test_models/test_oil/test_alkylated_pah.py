'''
    Test our Environment Canada Alkylated PAHs model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.oil import AlkylatedTotalPAH


class TestAlkylatedTotalPAH():
    def test_init_defaults(self):
        # basically everything has a default
        obj = AlkylatedTotalPAH()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.c0_n is None
        assert obj.c1_n is None
        assert obj.c2_n is None
        assert obj.c3_n is None
        assert obj.c4_n is None

        assert obj.c0_p is None
        assert obj.c1_p is None
        assert obj.c2_p is None
        assert obj.c3_p is None
        assert obj.c4_p is None

        assert obj.c0_d is None
        assert obj.c1_d is None
        assert obj.c2_d is None
        assert obj.c3_d is None

        assert obj.c0_f is None
        assert obj.c1_f is None
        assert obj.c2_f is None
        assert obj.c3_f is None

        assert obj.c0_b is None
        assert obj.c1_b is None
        assert obj.c2_b is None
        assert obj.c3_b is None
        assert obj.c4_b is None

        assert obj.c0_c is None
        assert obj.c1_c is None
        assert obj.c2_c is None
        assert obj.c3_c is None

        # Other Priority PAHs
        assert obj.biphenyl is None
        assert obj.acenaphthylene is None
        assert obj.acenaphthene is None
        assert obj.anthracene is None
        assert obj.fluoranthene is None
        assert obj.pyrene is None

        assert obj.benz_a_anthracene is None
        assert obj.benzo_b_fluoranthene is None
        assert obj.benzo_k_fluoranthene is None
        assert obj.benzo_e_pyrene is None
        assert obj.benzo_a_pyrene is None

        assert obj.perylene is None
        assert obj.indeno_1_2_3_cd_pyrene is None
        assert obj.dibenzo_ah_anthracene is None
        assert obj.benzo_ghi_perylene is None

    @pytest.mark.parametrize('weathering, method, pyrene',
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
                                  0.1, 'Method', 10.0,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, weathering, method, pyrene):
        # we will not test every attribute, just the ones that have
        # constraints
        obj = AlkylatedTotalPAH(weathering=weathering,
                                method=method,
                                pyrene=pyrene)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
        assert obj.pyrene.value == float(pyrene['value'])
        assert obj.pyrene.unit == str(pyrene['unit'])
