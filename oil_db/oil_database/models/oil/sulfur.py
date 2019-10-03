#
# PyMODM model class for Environment Canada's sulfur
# oil properties.
#
from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import FloatUnit


class Sulfur(MongoBaseModel):
    fraction: FloatUnit
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.fraction, self.weathering))
