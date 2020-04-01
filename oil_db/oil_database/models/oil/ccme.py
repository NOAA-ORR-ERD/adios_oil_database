"""
dataclass to hold the CCME data

CCME is kind of a special case, so this nails it down
"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )
from ..common.validators import (EnumValidator,
                                 )

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS

from dataclasses import dataclass, field
from datetime import datetime


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

    saturates:
    aromatics:
    GC_TPH:





