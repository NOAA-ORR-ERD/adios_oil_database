"""
NOTE: this really should be more extensivly tested!
"""

from dataclasses import dataclass

from oil_database.models.common.utilities import (JSON_List,
                                                  dataclass_to_json)


# A few examples to work with

@dataclass_to_json
@dataclass
class ReallySimple:
    x: int = None
    thing: str = ""


def test_simple_py_json():
    rs = ReallySimple(x=5, thing="fred")

    py_json = rs.py_json()

    assert py_json['x'] == 5
    assert py_json['thing'] == "fred"


def test_simple_from_py_json():
    rs = ReallySimple.from_py_json({'x': 5,
                                    'thing': "fred"}
                                   )

    assert type(rs) is ReallySimple

    assert rs.x == 5
    assert rs.thing == "fred"



