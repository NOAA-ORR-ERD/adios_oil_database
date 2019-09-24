from .adhesion import ECAdhesion
from .alkanes import ECNAlkanes
from .interfacial_tension import ECInterfacialTension
from .flash_point import ECFlashPoint
from .pour_point import ECPourPoint
from .emulsion import ECEmulsion
from .sulfur import ECSulfur
from .water import ECWater
from .benzene import ECBenzene
from .wax import ECWax

from .imported_rec import ECImportedRecord


__all__ = [
           ECAdhesion,
           ECNAlkanes,
           ECInterfacialTension,
           ECFlashPoint,
           ECPourPoint,
           ECEmulsion,
           ECSulfur,
           ECWater,
           ECBenzene,
           ECWax,
           ECImportedRecord,
           ]
