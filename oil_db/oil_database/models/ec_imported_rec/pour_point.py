#
# Model class for Environment Canada's pour point
# oil properties.
#
from pydantic import BaseModel, constr

from oil_database.models.common.float_unit import TemperatureUnit


class ECPourPoint(BaseModel):
    ref_temp: TemperatureUnit = None
    weathering: float = 0.0

    # may as well keep the extra stuff
    standard_deviation: float = None
    replicates: float = None
    method: constr(max_length=32) = None

    def __repr__(self):
        w = self.weathering

        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.ref_temp, w))
