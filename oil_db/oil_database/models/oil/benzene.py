#
# PyMODM model class for benzene oil properties.
#
from pydantic import BaseModel, constr

# we are probably not talking about concentrations of benzene in water here,
# but the units we are dealing with are the same.
from oil_database.models.common.float_unit import ConcentrationInWaterUnit


class Benzene(BaseModel):
    weathering: float = 0.0
    method: constr(max_length=16) = None

    benzene: ConcentrationInWaterUnit = None
    toluene: ConcentrationInWaterUnit = None
    ethylbenzene: ConcentrationInWaterUnit = None
    m_p_xylene: ConcentrationInWaterUnit = None
    o_xylene: ConcentrationInWaterUnit = None

    isopropylbenzene: ConcentrationInWaterUnit = None
    propylebenzene: ConcentrationInWaterUnit = None
    isobutylbenzene: ConcentrationInWaterUnit = None
    amylbenzene: ConcentrationInWaterUnit = None
    n_hexylbenzene: ConcentrationInWaterUnit = None

    x1_2_3_trimethylbenzene: ConcentrationInWaterUnit = None
    x1_2_4_trimethylbenzene: ConcentrationInWaterUnit = None
    x1_2_dimethyl_4_ethylbenzene: ConcentrationInWaterUnit = None
    x1_3_5_trimethylbenzene: ConcentrationInWaterUnit = None
    x1_methyl_2_isopropylbenzene: ConcentrationInWaterUnit = None
    x2_ethyltoluene: ConcentrationInWaterUnit = None
    x3_4_ethyltoluene: ConcentrationInWaterUnit = None

    def __repr__(self):
        return ('<{}(benzene={}, w={})>'
                .format(self.__class__.__name__,
                        self.benzene, self.weathering))
