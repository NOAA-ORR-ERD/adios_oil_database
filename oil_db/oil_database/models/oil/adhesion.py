#
# PyMODM model class for Environment Canada's adhesion
# oil properties.
#
from pydantic import BaseModel, constr

from oil_database.models.common.float_unit import AdhesionUnit


class Adhesion(BaseModel):
    adhesion: AdhesionUnit
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({}, w={})>'
                .format(self.__class__.__name__,
                        self.adhesion, self.weathering))
