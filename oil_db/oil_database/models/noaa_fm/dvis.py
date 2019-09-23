#
# Model class definitions for embedded content in our oil records
#

from pydantic import BaseModel, constr


class NoaaFmDVis(BaseModel):
    kg_ms: float
    ref_temp_k: float
    weathering: float = 0.0

    replicates: float = None
    standard_deviation: float = None
    method: constr(max_length=20) = None

    def __repr__(self):
        return ('<NoaaFmDVis({0.kg_ms} kg/ms at {0.ref_temp_k}K, '
                'w={0.weathering})>'
                .format(self))
