"""
tests for the version object
"""

from dataclasses import dataclass, field
from adios_db.models.common.utilities import dataclass_to_json

from adios_db.models.oil.version import Version

import pytest

def test_init():
    v = Version(1, 2, 3)

    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3


def test_string_init():
    v = Version(1, 2, 10) == Version("1.2.10")


def test_too_many_parts():
    with pytest.raises(TypeError):
        v = Version(1, 2, 3, 4)


def test_str():
    v = Version(1, 2, 3)

    assert str(v) == "1.2.3"


def test_repr_():
    assert repr(Version(8, 9)) == "Version(8, 9, 0)"


def test_py_json():
    v = Version(1, 12, 0)

    pyjs = v.py_json()

    assert pyjs == "1.12.0"


def test_from_py_json():
    v = Version.from_py_json("3.4.2")
    assert v.major == 3
    assert v.minor == 4
    assert v.patch == 2

def test_from_py_json_wrong_type():
    with pytest.raises(ValueError):
        v = Version.from_py_json(1.2)


def test_round_trip():
    v = Version(1, 2, 3)
    v2 = Version.from_py_json(v.py_json())

    assert v == v2


def test_equal():
    v1 = Version(1,2,3)
    v2 = Version(1,2,3)

    assert v1 == v2
    assert v1 <= v2
    assert v1 >= v2


def test_greater_than():
    v1 = Version(1,2,3)
    v2 = Version(1,2,2)

    assert v1 > v2
    assert v1 >= v2


def test_less_than():
    v1 = Version(1,2,3)
    v2 = Version(1,2,2)

    assert v2 < v1
    assert v2 <= v1


# a really simple test of putting it in a json_dataclass
@dataclass_to_json
@dataclass
class Simple:
    x: int
    version: Version
    name: str = ""


def test_inside_a_dataclass():
    s = Simple(5, name="fred", version=Version("4.7.2"))

    print(s)

    assert s.x == 5
    assert str(s.version) == "4.7.2"


def test_inside_a_dataclass_py_json():
    s = Simple(5, version=Version(7, 8, 9), name="fred")

    print(s)

    pyjs = s.py_json()

    print(pyjs)
    assert pyjs['x'] == 5
    assert pyjs['name'] == 'fred'
    assert pyjs['version'] == '7.8.9'


def test_inside_a_dataclass_from_py_json():
    s = Simple.from_py_json({'x': 5, 'name': 'fred', 'version': '3.4.5'})

    assert s == Simple(5, name="fred", version=Version(3, 4, 5))


def test_round_trip():
    s = Simple(5, name="fred", version=Version(5, 6, 0))

    pyjs = s.py_json()

    s2 = Simple.from_py_json(pyjs)

    assert s == s2





