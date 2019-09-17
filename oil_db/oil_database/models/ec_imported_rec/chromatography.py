#
# PyMODM model class for Environment Canada's gas chromatography
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import CharField, FloatField


class ECGasChromatography(EmbeddedMongoModel):
    '''
        Gas Chromatography (ESTS 2002a):
        - Total Petroleum Hydrocarbons (mg/g)
        - Total Saturate Hydrocarbons (mg/g)
        - Total Aromatic Hydrocarbons (mg/g)
        - Hydrocarbon Content Ratios
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    tph_mg_g = FloatField(blank=True)
    tsh_mg_g = FloatField(blank=True)
    tah_mg_g = FloatField(blank=True)

    tsh_tph_percent = FloatField(blank=True)
    tah_tph_percent = FloatField(blank=True)
    resolved_peaks_tph_percent = FloatField(blank=True)

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        if 'weathering' not in kwargs or kwargs['weathering'] is None:
            # Seriously?  What good is a default if it can't negotiate
            # None values?
            kwargs['weathering'] = 0.0

        super(ECGasChromatography, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'tph={0.tph_mg_g} mg/g, '
                'tsh={0.tsh_mg_g} mg/g, '
                'tah={0.tah_mg_g} mg/g, '
                'tsh_tph={0.tsh_tph_percent}%, '
                'tah_tph={0.tah_tph_percent}%, '
                'resolved_peaks_tph={0.resolved_peaks_tph_percent}%, '
                'weathering={0.weathering})>'
                .format(self))
