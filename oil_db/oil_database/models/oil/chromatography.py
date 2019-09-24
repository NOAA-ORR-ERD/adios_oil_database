#
# PyMODM model class for gas chromatography oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import (FloatUnit,
                                                   ConcentrationInWaterUnit)


class GasChromatography(BaseModel):
    '''
        Gas Chromatography (ESTS 2002a):
        - Total Petroleum Hydrocarbons (mg/g)
        - Total Saturate Hydrocarbons (mg/g)
        - Total Aromatic Hydrocarbons (mg/g)
        - Hydrocarbon Content Ratios
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    tph: ConcentrationInWaterUnit = None
    tsh: ConcentrationInWaterUnit = None
    tah: ConcentrationInWaterUnit = None

    tsh_tph: FloatUnit = None
    tah_tph: FloatUnit = None
    resolved_peaks_tph: FloatUnit = None

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
