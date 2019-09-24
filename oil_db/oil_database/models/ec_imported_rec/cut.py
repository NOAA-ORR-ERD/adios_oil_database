#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr


class ECCut(BaseModel):
    percent: float
    temp_c: float = None
    weathering: float = 0.0

    method: constr(max_length=48) = None

    def __repr__(self):
        return ('<{}({}% at {}C, w={})>'
                .format(self.__class__.__name__,
                        self.percent, self.temp_c, self.weathering))
