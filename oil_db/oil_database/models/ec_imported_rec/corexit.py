#
# Model class for Environment Canada's emulsion
# oil properties.
#
from oil_database.models.common import MongoBaseModel
from oil_database.models.common.float_unit import FloatUnit


class ECCorexit9500(MongoBaseModel):
    '''
        Chemical dispersability with Corexit 9500 Dispersant (swirling flask
        test) (ASTM F2059)
    '''
    dispersant_effectiveness: FloatUnit = None
    weathering: float = 0.0

    # may as well keep the extra stuff
    standard_deviation: float = None
    replicates: float = None

    def __repr__(self):
        return ('<{}(effectiveness={}%, w={})>'
                .format(self.__class__.__name__,
                        self.dispersant_effectiveness, self.weathering))
