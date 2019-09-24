#
# PyMODM model class for water content oil properties.
#
from pydantic import BaseModel

from oil_database.models.common.float_unit import FloatUnit


class Water(BaseModel):
    fraction: FloatUnit
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.fraction, self.weathering))
