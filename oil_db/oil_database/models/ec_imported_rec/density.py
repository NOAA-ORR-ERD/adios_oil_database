#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr


class ECDensity(BaseModel):
    g_ml: float
    ref_temp_c: float
    weathering: float = 0.0

    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<ECDensity({0.g_ml} g/mL at {0.ref_temp_c}C, '
                'w={0.weathering})>'
                .format(self))
