#
# Model class definitions for embedded content in our oil records
#

from pydantic import BaseModel


class NoaaFmKVis(BaseModel):
    m_2_s: float
    ref_temp_k: float
    weathering: float = 0.0

    def __repr__(self):
        return ('<NoaaFmKVis({0.m_2_s} m^2/s at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
