"""
NOTE: this really should be more extensivly tested!
"""

from dataclasses import dataclass, field

from oil_database.models.common.utilities import (JSON_List,
                                                  dataclass_to_json)

import pytest

# A few examples to work with

@dataclass_to_json
@dataclass
class ReallySimple:
    x: int = None
    thing: str = ""

@dataclass_to_json
@dataclass
class NestedList:
    these: JSON_List = field(default_factory=JSON_List)
    those: JSON_List = field(default_factory=JSON_List)


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


def test_add_extra_attribute():
        rs = ReallySimple.from_py_json({'x': 5,
                                    'thing': "fred"}
                                   )

        with pytest.raises(AttributeError):
            rs.something_random = 42


def test_json_list():
    # at least make sure it acts like a list
    assert JSON_List() == []

    assert JSON_List([1, 2, 3, 4]) == [1, 2, 3, 4]

    assert JSON_List((1, 2, 3, 4)) == [1, 2, 3, 4]

    jl = JSON_List((1, 2, 3, 4))
    jl.append(5)
    assert jl == [1, 2, 3, 4, 5]


def test_json_list_repr():
    jl = JSON_List([1, 2, 3, 4])

    assert repr(jl) == "JSON_List([1, 2, 3, 4])"


def test_json_list_pyjson_simple():
    jl = JSON_List((1, 2, 3, 4))

    assert jl.py_json() == [1, 2, 3, 4]


def test_json_list_pyjson_nested():
    jl = JSON_List([ReallySimple(x=5, thing="fred"),
                    ReallySimple(x=2, thing="bob"),
                    ReallySimple(x=1, thing="jane"),
                    ])

    pyjson = jl.py_json()

    print(pyjson)

    assert pyjson == [{'x': 5, 'thing': 'fred'},
                      {'x': 2, 'thing': 'bob'},
                      {'x': 1, 'thing': 'jane'},
                      ]

def test_nested_list_empty():
    nl = NestedList(these=[3, 4, 5])

    print(nl)
    print(nl.these)

    assert nl.these == [3, 4, 5]
    assert nl.those == []

    nl.those.extend([3, 4, 5])
    assert nl.those == [3, 4, 5]


def test_nested_list():
    nl = NestedList(these=JSON_List([ReallySimple(x=2, thing="bob"),
                                     ReallySimple(x=1, thing="jane"),
                                     ]))

    nl.those.extend([ReallySimple(x=5, thing="fred"),
                     ReallySimple(x=2, thing="bob"),
                     ReallySimple(x=1, thing="jane"),
                     ])

    print(nl)

    pyjson = nl.py_json()

    assert pyjson == {'these': [{'x': 2, 'thing': 'bob'},
                                {'x': 1, 'thing': 'jane'}],
                      'those': [{'x': 5, 'thing': 'fred'},
                                {'x': 2, 'thing': 'bob'},
                                {'x': 1, 'thing': 'jane'}]}


def test_nested_list_from_json():
    nl = NestedList.from_py_json({'these': [{'x': 2, 'thing': 'bob'},
                                            {'x': 1, 'thing': 'jane'}],
                                  'those': [{'x': 5, 'thing': 'fred'},
                                            {'x': 2, 'thing': 'bob'},
                                            {'x': 1, 'thing': 'jane'}]})

    print(nl)

    assert nl.these[0].x == 2
    assert nl.these[1].thing == 'jane'

    assert nl.those[0].thing == 'fred'
    assert nl.those[2].x == 1
