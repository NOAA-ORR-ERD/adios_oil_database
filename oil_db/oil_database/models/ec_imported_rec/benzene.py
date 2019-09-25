#
# Model class for Environment Canada's benzene
# oil properties.
#
from pydantic import BaseModel, constr


class ECBenzene(BaseModel):
    weathering: float = 0.0
    method: constr(max_length=16) = None

    benzene_ug_g: float = None
    toluene_ug_g: float = None
    ethylbenzene_ug_g: float = None
    m_p_xylene_ug_g: float = None
    o_xylene_ug_g: float = None

    isopropylbenzene_ug_g: float = None
    propylebenzene_ug_g: float = None
    isobutylbenzene_ug_g: float = None
    amylbenzene_ug_g: float = None
    n_hexylbenzene_ug_g: float = None

    x1_2_3_trimethylbenzene_ug_g: float = None
    x1_2_4_trimethylbenzene_ug_g: float = None
    x1_2_dimethyl_4_ethylbenzene_ug_g: float = None
    x1_3_5_trimethylbenzene_ug_g: float = None
    x1_methyl_2_isopropylbenzene_ug_g: float = None
    x2_ethyltoluene_ug_g: float = None
    x3_4_ethyltoluene_ug_g: float = None

    def __repr__(self):
        return ('<{}(benzene={} ug/g, w={})>'
                .format(self.__class__.__name__,
                        self.benzene_ug_g, self.weathering))
