#
# PyMODM model class for Environment Canada's gas chromatography
# oil properties.
#
from pymodm import EmbeddedMongoModel
from pymodm.fields import FloatField


class GasChromatography(EmbeddedMongoModel):
    '''
        Gas Chromatography (ESTS 2002a):
        - Total Petroleum Hydrocarbons (mg/g)
        - Total Saturate Hydrocarbons (mg/g)
        - Total Aromatic Hydrocarbons (mg/g)
        - Hydrocarbon Content Ratios
    '''
    weathering = FloatField(default=0.0)

    tph_mg_g = FloatField(blank=True)
    tsh_mg_g = FloatField(blank=True)
    tah_mg_g = FloatField(blank=True)

    tsh_tph_fraction = FloatField(blank=True)
    tah_tph_fraction = FloatField(blank=True)
    resolved_peaks_tph_fraction = FloatField(blank=True)

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

        super(GasChromatography, self).__init__(**kwargs)

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'tph_mg_g={0.tph_mg_g}, '
                'tsh_mg_g={0.tsh_mg_g}, '
                'tah_mg_g={0.tah_mg_g}, '
                'tsh_tph_fraction={0.tsh_tph_fraction}, '
                'tah_tph_fraction={0.tah_tph_fraction}, '
                'resolved_peaks_tph_fraction={0.resolved_peaks_tph_fraction}, '
                'weathering={0.weathering})>'
                .format(self))
