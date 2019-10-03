#
# PyMODM model class for Environment Canada's emulsion
# oil properties.
#
from pydantic import constr

from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import FloatUnit


class ChemicalDispersibility(MongoBaseModel):
    '''
        Chemical dispersability (swirling flask test) (ASTM F2059)
    '''
    dispersant: constr(max_length=20)
    effectiveness: FloatUnit
    weathering: float = 0.0

    # may as well keep the extra stuff
    standard_deviation: float = None
    replicates: float = None

    def __repr__(self):
        return ('<{}({}, effectiveness={}, w={})>'
                .format(self.__class__.__name__,
                        self.dispersant, self.effectiveness, self.weathering))
