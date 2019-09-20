#
# Model class definitions for embedded content in our oil records
#
from dataclasses import dataclass


@dataclass
class Synonym(object):
    name: str
