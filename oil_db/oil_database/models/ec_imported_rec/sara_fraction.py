#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr

from oil_database.models.common.enum_types import SaraTypeEnum


class ECSARAFraction(BaseModel):
    sara_type: SaraTypeEnum
    percent: float
    weathering: float = 0.0

    standard_deviation: float = None
    replicates: float = None
    method: constr(max_length=16) = None

    def __repr__(self):
        return ('<{}({}={}% w={})>'
                .format(self.__class__.__name__,
                        self.sara_type, self.percent, self.weathering))
