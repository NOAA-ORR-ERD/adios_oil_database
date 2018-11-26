#
# PyMODM model class for Environment Canada's alkylated total aromatic
# hydrocarbon oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class AlkylatedTotalPAH(EmbeddedMongoModel):
    '''
        Alkylated Total Aromatic Hydrocarbons (PAHs) (ug/g oil)
        (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)

    # Naphthalenes
    c0_n_ug_g = FloatField(blank=True)
    c1_n_ug_g = FloatField(blank=True)
    c2_n_ug_g = FloatField(blank=True)
    c3_n_ug_g = FloatField(blank=True)
    c4_n_ug_g = FloatField(blank=True)

    # Phenanthrenes
    c0_p_ug_g = FloatField(blank=True)
    c1_p_ug_g = FloatField(blank=True)
    c2_p_ug_g = FloatField(blank=True)
    c3_p_ug_g = FloatField(blank=True)
    c4_p_ug_g = FloatField(blank=True)

    # Dibenzothiophenes
    c0_d_ug_g = FloatField(blank=True)
    c1_d_ug_g = FloatField(blank=True)
    c2_d_ug_g = FloatField(blank=True)
    c3_d_ug_g = FloatField(blank=True)

    # Fluorenes
    c0_f_ug_g = FloatField(blank=True)
    c1_f_ug_g = FloatField(blank=True)
    c2_f_ug_g = FloatField(blank=True)
    c3_f_ug_g = FloatField(blank=True)

    # Benzonaphthothiophenes
    c0_b_ug_g = FloatField(blank=True)
    c1_b_ug_g = FloatField(blank=True)
    c2_b_ug_g = FloatField(blank=True)
    c3_b_ug_g = FloatField(blank=True)
    c4_b_ug_g = FloatField(blank=True)

    # Chrysenes
    c0_c_ug_g = FloatField(blank=True)
    c1_c_ug_g = FloatField(blank=True)
    c2_c_ug_g = FloatField(blank=True)
    c3_c_ug_g = FloatField(blank=True)

    # Other Priority PAHs
    biphenyl_bph_ug_g = FloatField(blank=True)
    acenaphthylene_acl_ug_g = FloatField(blank=True)
    acenaphthene_ace_ug_g = FloatField(blank=True)
    anthracene_an_ug_g = FloatField(blank=True)
    fluoranthene_fl_ug_g = FloatField(blank=True)
    pyrene_py_ug_g = FloatField(blank=True)

    benz_a_anthracene_baa_ug_g = FloatField(blank=True)
    benzo_b_fluoranthene_bbf_ug_g = FloatField(blank=True)
    benzo_k_fluoranthene_bkf_ug_g = FloatField(blank=True)
    benzo_e_pyrene_bep_ug_g = FloatField(blank=True)
    benzo_a_pyrene_bap_ug_g = FloatField(blank=True)

    perylene_pe_ug_g = FloatField(blank=True)
    indeno_1_2_3_cd_pyrene_ip_ug_g = FloatField(blank=True)
    dibenzo_ah_anthracene_da_ug_g = FloatField(blank=True)
    benzo_ghi_perylene_bgp_ug_g = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(AlkylatedTotalPAH, self).__init__(**kwargs)

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
                '{0.c3_d_ug_g}, '
                '{0.c4_d_ug_g}], '
                'Fluorenes='
                '[{0.c0_f_ug_g}, '
                '{0.c1_f_ug_g}, '
                '{0.c2_f_ug_g}, '
                '{0.c3_f_ug_g}, '
                '{0.c4_f_ug_g}], '
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
                '{0.c3_c_ug_g}, '
                '{0.c4_c_ug_g}], '
                'weathering={0.weathering})>'
                .format(self))
