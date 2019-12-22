"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


def _py_json(self, sparse=True):
    """
    function to convert a dataclass to json compatible python

    :param sparse=True: If sparse is True, only non-empty fields will be
                        written. If False, then all fields will be included.
    """
    json_obj = {}
    for fieldname in self.__dataclass_fields__.keys():
        val = getattr(self, fieldname)
        try:
            json_obj[fieldname] = val.py_json(sparse=sparse)
        except AttributeError:
            if not sparse:
                json_obj[fieldname] = val
            elif not (val == "" or val is None or val == []):
                # can't just use falsey -- zero is falsey, but also a valid value.
                json_obj[fieldname] = val
    return json_obj

class JSON_List(list):
    """
    just like a list, but with the ability to turn it into JSON

    A regular list can only be converted to JSON if it has
    JSON-able objects in it.
    """
    def py_json(self, sparse=True):
        json_obj = []
        for item in self:
            try:
                json_obj.append(item.py_json(sparse))
            except AttributeError:
                json_obj.append(item)
        return json_obj


def dataclass_to_json(cls):
    """
    class decorator that adds the ability to save a dataclass as JSON

    All fields must be either JSON-able Python types or
    have be a type with a _to_json method
    """
    cls.py_json = _py_json
    return cls

@dataclass_to_json
@dataclass
class Sample:
    """
    represents the physical and chemical properties of particular sub sample.

    could be fresh oil, or weathered samples, or distillation cuts, or ...
    """
    # metadata:
    name: str = "Fresh, Unweathered Oil"
    short_name: str = "Fresh"
    fraction_weathered: float = None
    boiling_point_range: tuple = None

    # should we use unit types here?
    densities: List = field(default_factory=list)
    kvis:   List = field(default_factory=list)


def list_of_samples():
    """
    create a list with one sample -- to use as a factory function
    """
    return JSON_List([Sample()])

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
    samples: List[Sample] = field(default_factory=list_of_samples)

    def __post_init__(self):
        """
        put any validation code here (__init__ is auto-gnerated by dataclass)

        right now, a non-empty name is it.
        """
        if self.name == "":
            raise TypeError("name must be a non-empty string")





