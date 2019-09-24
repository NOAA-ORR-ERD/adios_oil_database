#
# PyMODM Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr

from oil_database.models.common.float_unit import TemperatureUnit, FloatUnit


class Cut(BaseModel):
    fraction: FloatUnit
    vapor_temp: TemperatureUnit
    liquid_temp: TemperatureUnit = None
    weathering: float = 0.0

    method: constr(max_length=48) = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'liquid_temp={0.liquid_temp}, '
                'vapor_temp={0.vapor_temp}, '
                'f={0.fraction}, w={0.weathering})>'
                .format(self))
