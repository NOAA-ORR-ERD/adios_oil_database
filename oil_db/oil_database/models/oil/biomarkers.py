#
# PyMODM model class for Environment Canada's biomarker
# oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Biomarkers(EmbeddedMongoModel):
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
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(Biomarkers, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'c21_tricyclic_terpane={0.c21_tricyclic_terpane}, '
                'c22_tricyclic_terpane={0.c22_tricyclic_terpane}, '
                'c23_tricyclic_terpane={0.c23_tricyclic_terpane}, '
                'c24_tricyclic_terpane={0.c24_tricyclic_terpane}, '
                '_30_norhopane={0._30_norhopane}, '
                'hopane={0.hopane}, '
                '_30_homohopane_22s={0._30_homohopane_22s}, '
                '_30_homohopane_22r={0._30_homohopane_22r}, '
                '_30_31_bishomohopane_22s={0._30_31_bishomohopane_22s}, '
                '_30_31_bishomohopane_22r={0._30_31_bishomohopane_22r}, '
                '_30_31_trishomohopane_22s={0._30_31_trishomohopane_22s}, '
                '_30_31_trishomohopane_22r={0._30_31_trishomohopane_22r}, '
                'tetrakishomohopane_22s={0.tetrakishomohopane_22s}, '
                'tetrakishomohopane_22r={0.tetrakishomohopane_22r}, '
                'pentakishomohopane_22s={0.pentakishomohopane_22s}, '
                'pentakishomohopane_22r={0.pentakishomohopane_22r}, '
                '_18a_22_29_30_trisnorneohopane={0._18a_22_29_30_trisnorneohopane}, '
                '_17a_h_22_29_30_trisnorhopane={0._17a_h_22_29_30_trisnorhopane}, '
                '_14b_h_17b_h_20_cholestane={0._14b_h_17b_h_20_cholestane}, '
                '_14b_h_17b_h_20_methylcholestane={0._14b_h_17b_h_20_methylcholestane}, '
                '_14b_h_17b_h_20_ethylcholestane={0._14b_h_17b_h_20_ethylcholestane}, '
                'weathering={0.weathering})>'
                .format(self))
