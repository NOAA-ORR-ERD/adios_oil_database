"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import (dataclass_to_json,
                                JSON_List,
                                )

from .sample import Sample, list_of_samples

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

@dataclass_to_json
@dataclass
class Oil:
    # NOTE: types for documentation only -- not enforced
    # metadata:
    name: str  # only required field
    oil_id: str = ""
    location: str = ""
    reference: str = ""
    reference_date: int = ""
    sample_date: datetime = ""
    comments: str = ""
    labels: List[str] = field(default_factory=list)
    status: List[str] = field(default_factory=list)

    api: float = None
    product_type: str = ""
    # fixme: this should really be "sub_samples"
    samples: List[Sample] = field(default_factory=list)
    extra_data: Dict = field(default_factory=dict)

    def __post_init__(self):
        """
        put any validation code here (__init__ is auto-gnerated by dataclass)

        right now, a non-empty name is it.
        """
        if self.name == "":
            raise TypeError("name must be a non-empty string")

    def __setattr__(self, name, val):
        if name not in self.__dataclass_fields__:
            print("that's a new one!")
            raise AttributeError("You can only set existing attributes")
        else:
            print("setting:", name)
            self.__dict__[name] = val



