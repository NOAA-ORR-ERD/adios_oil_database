#
# PyMODM Model class definitions for embedded content in our oil records
#
from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import (TemperatureUnit,
                                                   DynamicViscosityUnit)


class DVis(MongoBaseModel):
    viscosity: DynamicViscosityUnit
    ref_temp: TemperatureUnit
    weathering: float = 0.0

    method: constr(max_length=32) = None
    replicates: float = None
    standard_deviation: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '({0.viscosity} at {0.ref_temp}, w={0.weathering})>'
                .format(self))
