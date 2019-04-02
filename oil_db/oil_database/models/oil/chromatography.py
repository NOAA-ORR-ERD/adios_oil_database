#
# PyMODM model class for gas chromatography oil properties.
#
from pymodm import EmbeddedMongoModel, EmbeddedDocumentField
from pymodm.fields import CharField, FloatField

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import (FloatUnit,
                                                   ConcentrationInWaterUnit)


class GasChromatography(EmbeddedMongoModel):
    '''
        Gas Chromatography (ESTS 2002a):
        - Total Petroleum Hydrocarbons (mg/g)
        - Total Saturate Hydrocarbons (mg/g)
        - Total Aromatic Hydrocarbons (mg/g)
        - Hydrocarbon Content Ratios
    '''
    weathering = FloatField(default=0.0)
    method = CharField(max_length=16, blank=True)

    tph = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    tsh = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)
    tah = EmbeddedDocumentField(ConcentrationInWaterUnit, blank=True)

    tsh_tph = EmbeddedDocumentField(FloatUnit, blank=True)
    tah_tph = EmbeddedDocumentField(FloatUnit, blank=True)
    resolved_peaks_tph = EmbeddedDocumentField(FloatUnit, blank=True)

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'tph={0.tph}, '
                'tsh={0.tsh}, '
                'tah={0.tah}, '
                'tsh_tph={0.tsh_tph}, '
                'tah_tph={0.tah_tph}, '
                'resolved_peaks_tph={0.resolved_peaks_tph}, '
                'weathering={0.weathering})>'
                .format(self))
