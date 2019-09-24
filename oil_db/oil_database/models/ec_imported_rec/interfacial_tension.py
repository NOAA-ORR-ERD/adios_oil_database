#
# Model class for Environment Canada's interfacial tension
# oil properties.
#
from pydantic import BaseModel, constr

from oil_database.models.common.enum_types import InterfaceTypeEnum


class ECInterfacialTension(BaseModel):
    dynes_cm: float
    ref_temp_c: float
    interface: InterfaceTypeEnum
    weathering: float = 0.0

    # may as well keep the extra stuff
    method: constr(max_length=32) = None
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<ECInterfacialTension({0.dynes_cm} dynes/cm '
                'at {0.ref_temp_c}C, '
                'if={0.interface}, w={0.weathering})>'
                .format(self))
