#
# Model class definitions for embedded content in our oil records
#

from pydantic import BaseModel


class NoaaFmDensity(BaseModel):
    kg_m_3: float
    ref_temp_k: float
    weathering: float = 0.0

    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<NoaaFmDensity({0.kg_m_3} kg/m^3 at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
