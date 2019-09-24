'''
    Test our Environment Canada Alkylated PAHs model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECAlkylatedTotalPAH


class TestECAlkylatedTotalPAH():
    def test_init_defaults(self):
        # basically everything has a default
        obj = ECAlkylatedTotalPAH()

        assert obj.weathering == 0.0
        assert obj.method is None

        assert obj.c0_n_ug_g is None
        assert obj.c1_n_ug_g is None
        assert obj.c2_n_ug_g is None
        assert obj.c3_n_ug_g is None
        assert obj.c4_n_ug_g is None

        assert obj.c0_p_ug_g is None
        assert obj.c1_p_ug_g is None
        assert obj.c2_p_ug_g is None
        assert obj.c3_p_ug_g is None
        assert obj.c4_p_ug_g is None

        assert obj.c0_d_ug_g is None
        assert obj.c1_d_ug_g is None
        assert obj.c2_d_ug_g is None
        assert obj.c3_d_ug_g is None

        assert obj.c0_f_ug_g is None
        assert obj.c1_f_ug_g is None
        assert obj.c2_f_ug_g is None
        assert obj.c3_f_ug_g is None

        assert obj.c0_b_ug_g is None
        assert obj.c1_b_ug_g is None
        assert obj.c2_b_ug_g is None
        assert obj.c3_b_ug_g is None
        assert obj.c4_b_ug_g is None

        assert obj.c0_c_ug_g is None
        assert obj.c1_c_ug_g is None
        assert obj.c2_c_ug_g is None
        assert obj.c3_c_ug_g is None

        # Other Priority PAHs
        assert obj.biphenyl_ug_g is None
        assert obj.acenaphthylene_ug_g is None
        assert obj.acenaphthene_ug_g is None
        assert obj.anthracene_ug_g is None
        assert obj.fluoranthene_ug_g is None
        assert obj.pyrene_ug_g is None

        assert obj.benz_a_anthracene_ug_g is None
        assert obj.benzo_b_fluoranthene_ug_g is None
        assert obj.benzo_k_fluoranthene_ug_g is None
        assert obj.benzo_e_pyrene_ug_g is None
        assert obj.benzo_a_pyrene_ug_g is None

        assert obj.perylene_ug_g is None
        assert obj.indeno_1_2_3_cd_pyrene_ug_g is None
        assert obj.dibenzo_ah_anthracene_ug_g is None
        assert obj.benzo_ghi_perylene_ug_g is None

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
        # we will not test every attribute, just the ones that have
        # constraints
        obj = ECAlkylatedTotalPAH(weathering=weathering,
                                  method=method)

        assert obj.weathering == float(weathering)
        assert obj.method == str(method)
