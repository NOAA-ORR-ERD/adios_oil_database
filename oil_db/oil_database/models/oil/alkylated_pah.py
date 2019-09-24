#
# PyMODM model class for Environment Canada's alkylated total aromatic
# hydrocarbon oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class AlkylatedTotalPAH(BaseModel):
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

    c0_n: ConcentrationInWaterUnit = None
    c1_n: ConcentrationInWaterUnit = None
    c2_n: ConcentrationInWaterUnit = None
    c3_n: ConcentrationInWaterUnit = None
    c4_n: ConcentrationInWaterUnit = None

    c0_p: ConcentrationInWaterUnit = None
    c1_p: ConcentrationInWaterUnit = None
    c2_p: ConcentrationInWaterUnit = None
    c3_p: ConcentrationInWaterUnit = None
    c4_p: ConcentrationInWaterUnit = None

    c0_d: ConcentrationInWaterUnit = None
    c1_d: ConcentrationInWaterUnit = None
    c2_d: ConcentrationInWaterUnit = None
    c3_d: ConcentrationInWaterUnit = None

    c0_f: ConcentrationInWaterUnit = None
    c1_f: ConcentrationInWaterUnit = None
    c2_f: ConcentrationInWaterUnit = None
    c3_f: ConcentrationInWaterUnit = None

    c0_b: ConcentrationInWaterUnit = None
    c1_b: ConcentrationInWaterUnit = None
    c2_b: ConcentrationInWaterUnit = None
    c3_b: ConcentrationInWaterUnit = None
    c4_b: ConcentrationInWaterUnit = None

    c0_c: ConcentrationInWaterUnit = None
    c1_c: ConcentrationInWaterUnit = None
    c2_c: ConcentrationInWaterUnit = None
    c3_c: ConcentrationInWaterUnit = None

    # Other Priority PAHs
    biphenyl: ConcentrationInWaterUnit = None
    acenaphthylene: ConcentrationInWaterUnit = None
    acenaphthene: ConcentrationInWaterUnit = None
    anthracene: ConcentrationInWaterUnit = None
    fluoranthene: ConcentrationInWaterUnit = None
    pyrene: ConcentrationInWaterUnit = None

    benz_a_anthracene: ConcentrationInWaterUnit = None
    benzo_b_fluoranthene: ConcentrationInWaterUnit = None
    benzo_k_fluoranthene: ConcentrationInWaterUnit = None
    benzo_e_pyrene: ConcentrationInWaterUnit = None
    benzo_a_pyrene: ConcentrationInWaterUnit = None

    perylene: ConcentrationInWaterUnit = None
    indeno_1_2_3_cd_pyrene: ConcentrationInWaterUnit = None
    dibenzo_ah_anthracene: ConcentrationInWaterUnit = None
    benzo_ghi_perylene: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'Naphthalenes='
                '[{0.c0_n}, '
                '{0.c1_n}, '
                '{0.c2_n}, '
                '{0.c3_n}, '
                '{0.c4_n}], '
                'Phenanthrenes='
                '[{0.c0_p}, '
                '{0.c1_p}, '
                '{0.c2_p}, '
                '{0.c3_p}, '
                '{0.c4_p}], '
                'Dibenzothiophenes='
                '[{0.c0_d}, '
                '{0.c1_d}, '
                '{0.c2_d}, '
                '{0.c3_d}], '
                'Fluorenes='
                '[{0.c0_f}, '
                '{0.c1_f}, '
                '{0.c2_f}, '
                '{0.c3_f}], '
                'Benzonaphthothiophenes='
                '[{0.c0_b}, '
                '{0.c1_b}, '
                '{0.c2_b}, '
                '{0.c3_b}, '
                '{0.c4_b}], '
                'Chrysenes='
                '[{0.c0_c}, '
                '{0.c1_c}, '
                '{0.c2_c}, '
                '{0.c3_c}], '
                'weathering={0.weathering})>'
                .format(self))
