#
# Model class for Environment Canada's adhesion
# oil properties.
#
from pydantic import BaseModel


class ECAdhesion(BaseModel):
    g_cm_2: float
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({} g/cm^2, w={})>'
                .format(self.__class__.__name__, self.g_cm_2, self.weathering))
