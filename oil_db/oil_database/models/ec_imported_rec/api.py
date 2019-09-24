#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel


class ECApiGravity(BaseModel):
    gravity: float
    weathering: float = 0.0

    def __repr__(self):
        return ('<ECApiGravity(g={0.gravity}, w={0.weathering})>'
                .format(self))
