#
# Model class for Environment Canada's alkylated total aromatic
# hydrocarbon oil properties.
#
from pydantic import BaseModel, constr


class ECAlkylatedTotalPAH(BaseModel):
    '''
        Alkylated Total Aromatic Hydrocarbons (PAHs) (ug/g oil)
        (ESTS 2002a)
        - c[0-4]_n_ug_g = Naphthalenes
        - c[0-4]_p_ug_g = Phenanthrenes
        - c[0-4]_d_ug_g = Dibenzothiophenes
        - c[0-4]_f_ug_g = Fluorenes
        - c[0-4]_b_ug_g = Benzonaphthothiophenes
        - c[0-4]_c_ug_g = Chrysenes
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    c0_n_ug_g: float = None
    c1_n_ug_g: float = None
    c2_n_ug_g: float = None
    c3_n_ug_g: float = None
    c4_n_ug_g: float = None

    c0_p_ug_g: float = None
    c1_p_ug_g: float = None
    c2_p_ug_g: float = None
    c3_p_ug_g: float = None
    c4_p_ug_g: float = None

    c0_d_ug_g: float = None
    c1_d_ug_g: float = None
    c2_d_ug_g: float = None
    c3_d_ug_g: float = None

    c0_f_ug_g: float = None
    c1_f_ug_g: float = None
    c2_f_ug_g: float = None
    c3_f_ug_g: float = None

    c0_b_ug_g: float = None
    c1_b_ug_g: float = None
    c2_b_ug_g: float = None
    c3_b_ug_g: float = None
    c4_b_ug_g: float = None

    c0_c_ug_g: float = None
    c1_c_ug_g: float = None
    c2_c_ug_g: float = None
    c3_c_ug_g: float = None

    # Other Priority PAHs
    biphenyl_ug_g: float = None
    acenaphthylene_ug_g: float = None
    acenaphthene_ug_g: float = None
    anthracene_ug_g: float = None
    fluoranthene_ug_g: float = None
    pyrene_ug_g: float = None

    benz_a_anthracene_ug_g: float = None
    benzo_b_fluoranthene_ug_g: float = None
    benzo_k_fluoranthene_ug_g: float = None
    benzo_e_pyrene_ug_g: float = None
    benzo_a_pyrene_ug_g: float = None

    perylene_ug_g: float = None
    indeno_1_2_3_cd_pyrene_ug_g: float = None
    dibenzo_ah_anthracene_ug_g: float = None
    benzo_ghi_perylene_ug_g: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'Naphthalenes='
                '[{0.c0_n_ug_g}, '
                '{0.c1_n_ug_g}, '
                '{0.c2_n_ug_g}, '
                '{0.c3_n_ug_g}, '
                '{0.c4_n_ug_g}], '
                'Phenanthrenes='
                '[{0.c0_p_ug_g}, '
                '{0.c1_p_ug_g}, '
                '{0.c2_p_ug_g}, '
                '{0.c3_p_ug_g}, '
                '{0.c4_p_ug_g}], '
                'Dibenzothiophenes='
                '[{0.c0_d_ug_g}, '
                '{0.c1_d_ug_g}, '
                '{0.c2_d_ug_g}, '
                '{0.c3_d_ug_g}], '
                'Fluorenes='
                '[{0.c0_f_ug_g}, '
                '{0.c1_f_ug_g}, '
                '{0.c2_f_ug_g}, '
                '{0.c3_f_ug_g}], '
                'Benzonaphthothiophenes='
                '[{0.c0_b_ug_g}, '
                '{0.c1_b_ug_g}, '
                '{0.c2_b_ug_g}, '
                '{0.c3_b_ug_g}, '
                '{0.c4_b_ug_g}], '
                'Chrysenes='
                '[{0.c0_c_ug_g}, '
                '{0.c1_c_ug_g}, '
                '{0.c2_c_ug_g}, '
                '{0.c3_c_ug_g}], '
                'weathering={0.weathering})>'
                .format(self))
