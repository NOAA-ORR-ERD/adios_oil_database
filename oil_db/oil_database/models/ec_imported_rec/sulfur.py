#
# Model class for Environment Canada's sulfur
# oil properties.
#
from pydantic import BaseModel


class ECSulfur(BaseModel):
    percent: float
    weathering: float = 0.0

    # may as well keep the extra stuff
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{}({}%, w={})>'
                .format(self.__class__.__name__,
                        self.percent, self.weathering))
