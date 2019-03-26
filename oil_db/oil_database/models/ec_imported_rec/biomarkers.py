#
# PyMODM model class for Environment Canada's biomarker
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECBiomarkers(EmbeddedMongoModel):
    '''
        Biomarkers (ug/g) (ESTS 2002a)
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    c21_tricyclic_terpane_ug_g = FloatField(blank=True)
    c22_tricyclic_terpane_ug_g = FloatField(blank=True)
    c23_tricyclic_terpane_ug_g = FloatField(blank=True)
    c24_tricyclic_terpane_ug_g = FloatField(blank=True)

    _30_norhopane_ug_g = FloatField(blank=True)
    hopane_ug_g = FloatField(blank=True)
    _30_homohopane_22s_ug_g = FloatField(blank=True)
    _30_homohopane_22r_ug_g = FloatField(blank=True)

    _30_31_bishomohopane_22s_ug_g = FloatField(blank=True)
    _30_31_bishomohopane_22r_ug_g = FloatField(blank=True)

    _30_31_trishomohopane_22s_ug_g = FloatField(blank=True)
    _30_31_trishomohopane_22r_ug_g = FloatField(blank=True)

    tetrakishomohopane_22s_ug_g = FloatField(blank=True)
    tetrakishomohopane_22r_ug_g = FloatField(blank=True)

    pentakishomohopane_22s_ug_g = FloatField(blank=True)
    pentakishomohopane_22r_ug_g = FloatField(blank=True)

    _18a_22_29_30_trisnorneohopane_ug_g = FloatField(blank=True)
    _17a_h_22_29_30_trisnorhopane_ug_g = FloatField(blank=True)

    _14b_h_17b_h_20_cholestane_ug_g = FloatField(blank=True)
    _14b_h_17b_h_20_methylcholestane_ug_g = FloatField(blank=True)
    _14b_h_17b_h_20_ethylcholestane_ug_g = FloatField(blank=True)

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

        super(ECBiomarkers, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'c21_tricyclic_terpane={0.c21_tricyclic_terpane_ug_g}, '
                'c22_tricyclic_terpane={0.c22_tricyclic_terpane_ug_g}, '
                'c23_tricyclic_terpane={0.c23_tricyclic_terpane_ug_g}, '
                'c24_tricyclic_terpane={0.c24_tricyclic_terpane_ug_g}, '
                '_30_norhopane={0._30_norhopane_ug_g}, '
                'hopane={0.hopane_ug_g}, '
                '_30_homohopane_22s={0._30_homohopane_22s_ug_g}, '
                '_30_homohopane_22r={0._30_homohopane_22r_ug_g}, '
                '_30_31_bishomohopane_22s={0._30_31_bishomohopane_22s_ug_g}, '
                '_30_31_bishomohopane_22r={0._30_31_bishomohopane_22r_ug_g}, '
                '_30_31_trishomohopane_22s={0._30_31_trishomohopane_22s_ug_g}, '
                '_30_31_trishomohopane_22r={0._30_31_trishomohopane_22r_ug_g}, '
                'tetrakishomohopane_22s={0.tetrakishomohopane_22s_ug_g}, '
                'tetrakishomohopane_22r={0.tetrakishomohopane_22r_ug_g}, '
                'pentakishomohopane_22s={0.pentakishomohopane_22s_ug_g}, '
                'pentakishomohopane_22r={0.pentakishomohopane_22r_ug_g}, '
                '_18a_22_29_30_trisnorneohopane={0._18a_22_29_30_trisnorneohopane_ug_g}, '
                '_17a_h_22_29_30_trisnorhopane={0._17a_h_22_29_30_trisnorhopane_ug_g}, '
                '_14b_h_17b_h_20_cholestane={0._14b_h_17b_h_20_cholestane_ug_g}, '
                '_14b_h_17b_h_20_methylcholestane={0._14b_h_17b_h_20_methylcholestane_ug_g}, '
                '_14b_h_17b_h_20_ethylcholestane={0._14b_h_17b_h_20_ethylcholestane_ug_g}, '
                'weathering={0.weathering})>'
                .format(self))
