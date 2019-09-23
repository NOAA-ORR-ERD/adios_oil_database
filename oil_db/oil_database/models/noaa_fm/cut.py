#
# Model class definitions for embedded content in our oil records
#

from pydantic import BaseModel


class NoaaFmCut(BaseModel):
    fraction: float
    vapor_temp_k: float = None
    liquid_temp_k: float = None
    weathering: float = 0.0

    def __repr__(self):
        lt = '{}K'.format(self.liquid_temp_k) if self.liquid_temp_k else None
        vt = '{}K'.format(self.vapor_temp_k) if self.vapor_temp_k else None
        return ('<NoaaFmCut(liquid_temp={}, vapor_temp={}, fraction={}, w={})>'
                .format(lt, vt, self.fraction, self.weathering))
