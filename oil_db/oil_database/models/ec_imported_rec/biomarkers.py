#
# PyMODM model class for Environment Canada's biomarker
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class Biomarkers(EmbeddedMongoModel):
    '''
        Note: some of the attribute fields coming from the spreadsheet contain
              greek & latin unicode characters, hence their weird slugified
              names.
              - 0xceb1 => greek small alpha => a
              - 0xc39f => latin small sharp s => ss
    '''
    weathering = FloatField(default=0.0)

    c21_tricyclic_terpane_c21t_ppm = FloatField(blank=True)
    c22_tricyclic_terpane_c22t_ppm = FloatField(blank=True)
    c23_tricyclic_terpane_c23t_ppm = FloatField(blank=True)
    c24_tricyclic_terpane_c24t_ppm = FloatField(blank=True)

    _30_norhopane_h29_ppm = FloatField(blank=True)
    hopane_h30_ppm = FloatField(blank=True)
    _30_homohopane_22s_h31s_ppm = FloatField(blank=True)
    _30_homohopane_22r_h31r_ppm = FloatField(blank=True)

    _30_31_bishomohopane_22s_h32s_ppm = FloatField(blank=True)
    _30_31_bishomohopane_22r_h32r_ppm = FloatField(blank=True)

    _30_31_trishomohopane_22s_h33s_ppm = FloatField(blank=True)
    _30_31_trishomohopane_22r_h33r_ppm = FloatField(blank=True)

    tetrakishomohopane_22s_h34s_ppm = FloatField(blank=True)
    tetrakishomohopane_22r_h34r_ppm = FloatField(blank=True)

    pentakishomohopane_22s_h35s_ppm = FloatField(blank=True)
    pentakishomohopane_22r_h35r_ppm = FloatField(blank=True)

    _18a_22_29_30_trisnorneohopane_c27ts_ppm = FloatField(blank=True)
    _17a_h_22_29_30_trisnorhopane_c27tm_ppm = FloatField(blank=True)

    _14ss_h_17ss_h_20_cholestane_c27assss_ppm = FloatField(blank=True)
    _14ss_h_17ss_h_20_methylcholestane_c28assss_ppm = FloatField(blank=True)
    _14ss_h_17ss_h_20_ethylcholestane_c29assss_ppm = FloatField(blank=True)

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

    def __repr__(self):
        return ('<Biomarkers('
                'c21_tricyclic_terpane_c21t={0.c21_tricyclic_terpane_c21t_ppm}, '
                'c22_tricyclic_terpane_c22t={0.c22_tricyclic_terpane_c22t_ppm}, '
                'c23_tricyclic_terpane_c23t={0.c23_tricyclic_terpane_c23t_ppm}, '
                'c24_tricyclic_terpane_c24t={0.c24_tricyclic_terpane_c24t_ppm}, '
                '_30_norhopane_h29={0._30_norhopane_h29_ppm}, '
                'hopane_h30={0.hopane_h30_ppm}, '
                '_30_homohopane_22s_h31s={0._30_homohopane_22s_h31s_ppm}, '
                '_30_homohopane_22r_h31r={0._30_homohopane_22r_h31r_ppm}, '
                '_30_31_bishomohopane_22s_h32s={0._30_31_bishomohopane_22s_h32s_ppm}, '
                '_30_31_bishomohopane_22r_h32r={0._30_31_bishomohopane_22r_h32r_ppm}, '
                '_30_31_trishomohopane_22s_h33s={0._30_31_trishomohopane_22s_h33s_ppm}, '
                '_30_31_trishomohopane_22r_h33r={0._30_31_trishomohopane_22r_h33r_ppm}, '
                'tetrakishomohopane_22s_h34s={0.tetrakishomohopane_22s_h34s_ppm}, '
                'tetrakishomohopane_22r_h34r={0.tetrakishomohopane_22r_h34r_ppm}, '
                'pentakishomohopane_22s_h35s={0.pentakishomohopane_22s_h35s_ppm}, '
                'pentakishomohopane_22r_h35r={0.pentakishomohopane_22r_h35r_ppm}, '
                '_18a_22_29_30_trisnorneohopane_c27ts={0._18a_22_29_30_trisnorneohopane_c27ts_ppm}, '
                '_17a_h_22_29_30_trisnorhopane_c27tm={0._17a_h_22_29_30_trisnorhopane_c27tm_ppm}, '
                '_14ss_h_17ss_h_20_cholestane_c27assss={0._14ss_h_17ss_h_20_cholestane_c27assss_ppm}, '
                '_14ss_h_17ss_h_20_methylcholestane_c28assss={0._14ss_h_17ss_h_20_methylcholestane_c28assss_ppm}, '
                '_14ss_h_17ss_h_20_ethylcholestane_c29assss={0._14ss_h_17ss_h_20_ethylcholestane_c29assss_ppm}, '
                'weathering={0.weathering})>'
                .format(self))
