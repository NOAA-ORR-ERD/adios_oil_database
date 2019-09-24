#
# PyMODM Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel

from oil_database.models.common.float_unit import DensityUnit, TemperatureUnit


class Density(BaseModel):
    density: DensityUnit
    ref_temp: TemperatureUnit
    weathering: float = 0.0

    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.density} at {0.ref_temp}, w={0.weathering})>'
                .format(self))
