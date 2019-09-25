#
# Model class for Environment Canada's wax
# oil properties.
#
from pydantic import BaseModel, constr


class ECWax(BaseModel):
    percent: float
    weathering: float = 0.0

    # may as well keep the extra stuff
    method: constr(max_length=16) = None
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({}%, w={})>'
                .format(self.__class__.__name__,
                        self.percent, self.weathering))
