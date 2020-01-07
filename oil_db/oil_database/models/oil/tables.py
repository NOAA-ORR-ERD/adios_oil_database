"""
classes for managing "tabular" data.

There are a few types:

MultiTempTable: tables of values at temperatures -- as in density and viscosity

StaticTable: table of key:value pairs, where the keys are always the same. e.g. SARA

DynamicTable: table of key value pairs with arbitrary keys. e.g.

"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .values import (UnittedValue,
                     )


from dataclasses import dataclass, field
from typing import List, Dict




