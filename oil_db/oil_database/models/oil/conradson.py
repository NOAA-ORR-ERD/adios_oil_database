from pydantic import BaseModel

from oil_database.models.common.float_unit import FloatUnit


class Conradson(BaseModel):
    weathering: float = 0.0

    residue: FloatUnit = None
    crude: FloatUnit = None

    def __repr__(self):
        return ('<{}(residue={}, crude={}, w={})>'
                .format(self.__class__.__name__,
                        self.residue, self.crude, self.weathering))
