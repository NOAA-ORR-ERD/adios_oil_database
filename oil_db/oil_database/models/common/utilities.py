"""
Tools for helping make our data models.

So far: making dataclasses read/writable as JSON
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


def _py_json(self, sparse=True):
    """
    function to convert a dataclass to json compatible python

    :param sparse=True: If sparse is True, only non-empty fields will be
                        written. If False, then all fields will be included.

    NOTE: could we use the dataclasses built-in .asdict?
          It would not support sparse.
    """
    json_obj = {}
    for fieldname in self.__dataclass_fields__.keys():
        val = getattr(self, fieldname)
        try:
            json_obj[fieldname] = val.py_json(sparse=sparse)
        except AttributeError:
            if not sparse:
                json_obj[fieldname] = val
            elif not (val is None or (val in ("", [], {}))):
                #  can't just use falsey -- zero is falsey,
                #  but also a valid value.
                json_obj[fieldname] = val
    return json_obj


@classmethod
def _from_py_json(cls, py_json):
    """
    classmethod to create a dataclass from json compatible python data
    structure.
    """
    print("working with:", py_json)
    arg_dict = {}
    for fieldname, fieldobj in cls.__dataclass_fields__.items():
        if fieldname in py_json:
            try:  # see if it's "one of ours"
                arg_dict[fieldname] = fieldobj.type.from_py_json(py_json[fieldname])
            except AttributeError:
                # it's not, so we just use the value
                arg_dict[fieldname] = py_json[fieldname]
    print("argdict is:", arg_dict)
    obj = cls(**arg_dict)
    return obj

def __setattr__(self, name, val):
    if name not in self.__dataclass_fields__:
        raise AttributeError("You can only set existing attributes")
    else:
        self.__dict__[name] = val


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
    cls.from_py_json = _from_py_json
    cls.__setattr__ = __setattr__

    return cls
