"""
dataclass to hold the CCME data

CCME is kind of a special case, so this nails it down
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from .measurement import MassFraction
from .compound import CompoundList


@dataclass_to_json
@dataclass
class CCME:
    """
    hold the CCME data from env CA

    (https://www.ccme.ca/en/resources/canadian_environmental_quality_guidelines/index.html)
    """
    CCME_F1: MassFraction = None
    CCME_F2: MassFraction = None
    CCME_F3: MassFraction = None
    CCME_F4: MassFraction = None

    total_GC_TPH: MassFraction = None

    saturates: CompoundList = field(default_factory=CompoundList)
    aromatics: CompoundList = field(default_factory=CompoundList)
    GC_TPH: CompoundList = field(default_factory=CompoundList)
