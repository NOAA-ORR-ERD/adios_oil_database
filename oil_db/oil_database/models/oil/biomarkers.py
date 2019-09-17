#
# PyMODM model class for Environment Canada's biomarker
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

from oil_database.models.common.model_mixin import EmbeddedMongoModelMixin

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Biomarkers(EmbeddedMongoModel, EmbeddedMongoModelMixin):
    '''
        Biomarkers (ug/g) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    c21_tricyclic_terpane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                  blank=True)
    c22_tricyclic_terpane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                  blank=True)
    c23_tricyclic_terpane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                  blank=True)
    c24_tricyclic_terpane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                  blank=True)

    _30_norhopane = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    hopane = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    _30_homohopane_22s = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                               blank=True)
    _30_homohopane_22r = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                               blank=True)

    _30_31_bishomohopane_22s = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                     blank=True)
    _30_31_bishomohopane_22r = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                     blank=True)

    _30_31_trishomohopane_22s = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                      blank=True)
    _30_31_trishomohopane_22r = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                      blank=True)

    tetrakishomohopane_22s = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                   blank=True)
    tetrakishomohopane_22r = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                   blank=True)

    pentakishomohopane_22s = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                   blank=True)
    pentakishomohopane_22r = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                   blank=True)

    _18a_22_29_30_trisnorneohopane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                           blank=True)
    _17a_h_22_29_30_trisnorhopane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                          blank=True)

    _14b_h_17b_h_20_cholestane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                       blank=True)
    _14b_h_17b_h_20_methylcholestane = EmbeddedDocumentField(ConcentrationInWaterUnit,
                                                             blank=True)
    _14b_h_17b_h_20_ethylcholestane = EmbeddedDocumentField(ConcentrationInWaterUnit,
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

        super(Biomarkers, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'C21T={0.c21_tricyclic_terpane}, '
                'C22T={0.c22_tricyclic_terpane}, '
                'C23T={0.c23_tricyclic_terpane}, '
                'C24T={0.c24_tricyclic_terpane}, '
                'H29={0._30_norhopane}, '
                'H30={0.hopane}, '
                'H31S={0._30_homohopane_22s}, '
                'H31R={0._30_homohopane_22r}, '
                'H32S={0._30_31_bishomohopane_22s}, '
                'H32R={0._30_31_bishomohopane_22r}, '
                'H33S={0._30_31_trishomohopane_22s}, '
                'H33R={0._30_31_trishomohopane_22r}, '
                'H34S={0.tetrakishomohopane_22s}, '
                'H34R={0.tetrakishomohopane_22r}, '
                'H35S={0.pentakishomohopane_22s}, '
                'H35R={0.pentakishomohopane_22r}, '
                'C27Ts={0._18a_22_29_30_trisnorneohopane}, '
                'C27Tm={0._17a_h_22_29_30_trisnorhopane}, '
                'C27aBB={0._14b_h_17b_h_20_cholestane}, '
                'C28aBB={0._14b_h_17b_h_20_methylcholestane}, '
                'C29aBB={0._14b_h_17b_h_20_ethylcholestane}, '
                'weathering={0.weathering})>'
                .format(self))
