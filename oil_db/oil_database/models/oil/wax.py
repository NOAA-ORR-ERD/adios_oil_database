#
# PyMODM model class for Environment Canada's wax
# oil properties.
#
from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import FloatUnit


class Wax(MongoBaseModel):
    fraction: FloatUnit
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None
    method: constr(max_length=16) = None

    def __repr__(self):
        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.fraction, self.weathering))
