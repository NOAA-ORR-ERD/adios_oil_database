#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.enum_types import VisualStabilityEnum
from oil_database.models.common.float_unit import (FloatUnit,
                                                   TimeUnit,
                                                   TemperatureUnit,
                                                   AdhesionUnit,
                                                   DynamicViscosityUnit)


class Emulsion(MongoBaseModel):
    water_content: FloatUnit
    age: TimeUnit
    ref_temp: TemperatureUnit

    weathering: float = 0.0
    wc_standard_deviation: float = None
    wc_replicates: float = None

    # may as well keep the extra stuff
    visual_stability: VisualStabilityEnum = None

    complex_modulus: AdhesionUnit = None
    cm_standard_deviation: float = None

    storage_modulus: AdhesionUnit = None
    sm_standard_deviation: float = None

    loss_modulus: AdhesionUnit = None
    lm_standard_deviation: float = None

    tan_delta_v_e: float = None
    td_standard_deviation: float = None

    complex_viscosity: DynamicViscosityUnit = None
    cv_standard_deviation: float = None

    mod_replicates: float = None

    def __repr__(self):
        return ('<{}(water_content={}, temp={}, age={}, w={})>'
                .format(self.__class__.__name__,
                        self.water_content,
                        self.ref_temp, self.age, self.weathering))
