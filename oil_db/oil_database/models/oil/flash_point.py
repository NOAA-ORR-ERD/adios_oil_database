from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import TemperatureUnit


class FlashPoint(MongoBaseModel):
    ref_temp: TemperatureUnit = None
    weathering: float = 0.0

    # may as well keep the extra stuff
    standard_deviation: float = None
    replicates: float = None
    method: constr(max_length=32) = None

    def __repr__(self):
        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.ref_temp, self.weathering))
