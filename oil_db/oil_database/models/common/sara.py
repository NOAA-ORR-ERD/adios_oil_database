#
# PyMODM Model class definitions for embedded content in our oil records
#
from enum import Enum

from pydantic import BaseModel, constr


class SaraTypeEnum(str, Enum):
    saturates = 'Saturates'
    aromatics = 'Aromatics'
    resins = 'Resins'
    asphaltenes = 'Asphaltenes'


class SARAFraction(BaseModel):
    sara_type = SaraTypeEnum

    fraction: float
    ref_temp_k: float = 273.15
    weathering: float = 0.0

    standard_deviation: float = None
    replicates: float = None
    method: constr(max_length=16) = None


class SARADensity(BaseModel):
    sara_type = SaraTypeEnum

    kg_m_3: float
    ref_temp_k: float = 273.15
    weathering: float = 0.0


class MolecularWeight(BaseModel):
    sara_type = SaraTypeEnum

    g_mol: float
    ref_temp_k: float = 273.15
    weathering: float = 0.0

    @property
    def kg_mol(self):
        return self.g_mol / 1000.0

    @kg_mol.setter
    def length(self, value):
        self.g_mol = value * 1000.0
