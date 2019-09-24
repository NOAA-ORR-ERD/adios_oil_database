#
# Model class for Environment Canada's gas chromatography
# oil properties.
#
from pydantic import BaseModel, constr


class ECGasChromatography(BaseModel):
    '''
        Gas Chromatography (ESTS 2002a):
        - Total Petroleum Hydrocarbons (mg/g)
        - Total Saturate Hydrocarbons (mg/g)
        - Total Aromatic Hydrocarbons (mg/g)
        - Hydrocarbon Content Ratios
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    tph_mg_g: float = None
    tsh_mg_g: float = None
    tah_mg_g: float = None

    tsh_tph_percent: float = None
    tah_tph_percent: float = None
    resolved_peaks_tph_percent: float = None

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
