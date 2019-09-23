#
# Model class definitions for embedded content in our oil records
#
from pydantic import BaseModel


class Synonym(BaseModel):
    name: str
