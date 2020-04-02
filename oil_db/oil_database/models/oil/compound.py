"""
dataclass to store the compounds
"""

from dataclasses import dataclass, field

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .measurement import MassFraction

@dataclass_to_json
@dataclass
class Compound:

    name: str = ""
    groups: list = field(default_factory=list)
    method: str = ""
    measurement: MassFraction = None


class CompoundList(JSON_List):
    item_type = Compound
