#
# PyMODM Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr

from oil_database.models.common.enum_types import SaraTypeEnum
from oil_database.models.common.float_unit import FloatUnit


class SARAFraction(BaseModel):
    sara_type: SaraTypeEnum
    weathering: float = 0.0
    fraction: FloatUnit

    standard_deviation: float = None
    replicates: float = None
    method: constr(max_length=16) = None

    def __repr__(self):
        return ('<{}({}={} w={})>'
                .format(self.__class__.__name__,
                        self.sara_type, self.fraction, self.weathering))
