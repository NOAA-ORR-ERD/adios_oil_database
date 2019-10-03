from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.enum_types import InterfaceTypeEnum
from oil_database.models.common.float_unit import (TemperatureUnit,
                                                   InterfacialTensionUnit)


class InterfacialTension(MongoBaseModel):
    '''
        Interfacial tension model.
    '''
    tension: InterfacialTensionUnit
    ref_temp: TemperatureUnit
    interface: InterfaceTypeEnum
    weathering: float = 0.0

    # may as well keep the extra stuff
    method: constr(max_length=32) = None
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.tension} at {0.ref_temp}, '
                'if={0.interface}, w={0.weathering})>'
                .format(self))
