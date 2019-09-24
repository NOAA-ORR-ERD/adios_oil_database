#
# PyMODM Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel


class ApiGravity(BaseModel):
    gravity: float
    weathering: float = 0.0

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                '(g={0.gravity}, w={0.weathering})>'
                .format(self))
