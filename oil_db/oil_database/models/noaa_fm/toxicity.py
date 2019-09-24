#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel, constr

from oil_database.models.common.enum_types import ToxicityTypeEnum


class NoaaFmToxicity(BaseModel):
    tox_type: ToxicityTypeEnum
    species: constr(max_length=24)

    after_24h: float = None
    after_48h: float = None
    after_96h: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                '{0.species}, {0.tox_type}, '
                '[{0.after_24h}, {0.after_48h}, {0.after_96h}])>'
                .format(self))
