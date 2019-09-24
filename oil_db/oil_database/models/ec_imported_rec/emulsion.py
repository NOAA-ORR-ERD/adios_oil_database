#
# Model class for Environment Canada's emulsion
# oil properties.
#
from pydantic import BaseModel, constr

from oil_database.models.common.enum_types import VisualStabilityEnum


class ECEmulsion(BaseModel):
    water_content_percent: float
    wc_standard_deviation: float = None
    wc_replicates: float = None

    age_days: float
    ref_temp_c: float
    weathering: float = 0.0

    # may as well keep the extra stuff
    visual_stability: VisualStabilityEnum = None

    complex_modulus_pa: float = None
    cm_standard_deviation: float = None

    storage_modulus_pa: float = None
    sm_standard_deviation: float = None

    loss_modulus_pa: float = None
    lm_standard_deviation: float = None

    tan_delta_v_e: float = None
    td_standard_deviation: float = None

    complex_viscosity_pa_s: float = None
    cv_standard_deviation: float = None

    mod_replicates: float = None

    def __repr__(self):
        return ('<{}(water_percent={}, temp={}C, age={} days, w={})>'
                .format(self.__class__.__name__,
                        self.water_content_percent,
                        self.ref_temp_c, self.age_days, self.weathering))
