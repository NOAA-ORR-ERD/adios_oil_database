#
# PyMODM model class for Environment Canada's alkylated total aromatic
# hydrocarbon oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class AlkylatedTotalPAH(EmbeddedMongoModel, EmbeddedMongoModelMixin):
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
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    c0_n = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_n = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_n = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_n = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c4_n = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c0_p = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_p = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_p = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_p = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c4_p = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c0_d = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_d = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_d = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_d = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c0_f = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_f = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_f = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_f = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c0_b = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_b = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_b = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_b = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c4_b = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    c0_c = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c1_c = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c2_c = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    c3_c = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    # Other Priority PAHs
    biphenyl = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    acenaphthylene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                           blank=True)
    acenaphthene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    anthracene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    fluoranthene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    pyrene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    benz_a_anthracene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                              blank=True)
    benzo_b_fluoranthene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                 blank=True)
    benzo_k_fluoranthene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                 blank=True)
    benzo_e_pyrene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                           blank=True)
    benzo_a_pyrene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                           blank=True)

    perylene = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    indeno_1_2_3_cd_pyrene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                   blank=True)
    dibenzo_ah_anthracene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                  blank=True)
    benzo_ghi_perylene = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                               blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        self._set_embedded_property_args(kwargs)

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

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
