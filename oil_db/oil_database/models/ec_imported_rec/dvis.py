#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr

from oil_database.models.common.float_unit import DynamicViscosityUnit


class ECDVis(BaseModel):
    mpa_s: DynamicViscosityUnit
    ref_temp_c: float
    weathering: float = 0.0

    method: constr(max_length=32) = None
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<ECDVis({0.mpa_s} at {0.ref_temp_c}C, '
                'w={0.weathering})>'
                .format(self))
