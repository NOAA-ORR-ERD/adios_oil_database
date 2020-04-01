from math import isclose

import pytest

from unit_conversion import InvalidUnitError

from oil_database.models.oil.measurement import (Length,
                                                 Temperature)


#  Note: the Measurement base class should not be used on its own
#.       it needs a unit type
# so it's not tested here


def test_Length():
    uv = Length(1.0, unit="m")

    assert uv.value == 1.0
    assert uv.unit == "m"

# we can't have any required arguments
# as you could have value, or min or max
# def test_Length_no_value():
#     with pytest.raises(TypeError):
#         Length()

#     with pytest.raises(TypeError):
#         Length(unit="m/s")


# def test_Length_no_unit():
#     with pytest.raises(TypeError):
#         Length(1.0)


def test_Length_json():
    uv = Length(1.0, unit="m")

    py_json = uv.py_json()

    print(py_json)

    assert py_json == {'value': 1.0,
                       'unit': 'm',
                       'unit_type': 'length',
                       }


def test_Length_from_py_json():
    uv = Length.from_py_json({'value': 1.0, 'unit': 'm'})

    assert uv.value == 1.0
    assert uv.unit == "m"

# can't have any required data
# def test_Length_from_py_json_missing_data():

#     with pytest.raises(TypeError):
#         Length.from_py_json({'value': 1.0})

#     with pytest.raises(TypeError):
#         Length.from_py_json({'unit': 'm/s'})


def test_LengthRange_both():
    ur = Length(None, "ft", 1.0, 5.0)

    assert ur.min_value == 1.0
    assert ur.max_value == 5.0
    assert ur.unit == "ft"


def test_LengthRange_json_sparse():
    ur = Length(max_value=5.0, unit='m')

    py_json = ur.py_json()

    assert py_json == {'max_value': 5.0,
                       'unit': 'm',
                       'unit_type': 'length'}


def test_Length_json_full():
    l = Length(max_value=5.0, unit='m')

    py_json = l.py_json(sparse=False)

    print(l)
    print(l.py_json)
    assert py_json == {'value': None,
                       'max_value': 5.0,
                       'unit': 'm',
                       'min_value': None,
                       'standard_deviation': None,
                       'replicates': None,
                       'unit_type': 'length'}


def test_Length_from_json_min():
    ur = Length.from_py_json({'min_value': 5.0,
                              'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value is None
    assert ur.unit == "m/s"


def test_Length_range_from_json():
    ur = Length.from_py_json({'min_value': 5.0,
                              'max_value': 10.1,
                              'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value == 10.1
    assert ur.unit == "m/s"


def test_Length_convert_to():
    l = Length(1.0, unit="m")

    assert l.value == 1.0
    assert l.unit == "m"

    l.convert_to("ft")

    assert l.unit == "ft"
    assert isclose(l.value, 3.280839895)
    assert l.min_value is None
    assert l.max_value is None
    assert l.standard_deviation is None
    assert l.replicates is None


def test_Length_convert_to_all():
    l = Length(min_value=1.0,
               max_value=10.0,
               unit="m",
               replicates=3,
               standard_deviation=0.5)

    assert l.min_value == 1.0
    assert l.max_value == 10.0
    assert l.unit == "m"
    assert l.replicates == 3
    assert l.standard_deviation == 0.5

    l.convert_to("ft")

    assert l.unit == "ft"
    assert l.value is None

    assert isclose(l.min_value, 3.280839895)
    assert isclose(l.max_value, 32.80839895)
    assert isclose(l.standard_deviation, 1.6404199475)
    assert l.replicates == 3


def test_convert_wrong_unit():
    l = Length(min_value=1.0,
               max_value=10.0,
               unit="m",
               replicates=3,
               standard_deviation=0.5)

    with pytest.raises(InvalidUnitError):
        l.convert_to("kg")


def test_convert_wrong_unit_not_break():
    l = Length(min_value=1.0,
               max_value=10.0,
               unit="m",
               replicates=3,
               standard_deviation=0.5)
    # make sure an icorrect unit didn't break anything!
    try:
        l.convert_to("kg")
    except InvalidUnitError:
        assert l.min_value == 1.0
        assert l.max_value == 10.0
        assert l.unit == "m"
        assert l.replicates == 3
        assert l.standard_deviation == 0.5


def test_convert_wrong_value_not_break():
    l = Length(min_value=1.0,
               max_value=10.0,
               unit="m",
               replicates=3,
               standard_deviation="bad value")
    # make sure an icorrect unit didn't break anything!
    try:
        l.convert_to("cm")
    except: # anything goes wrong, the values shouldn't change
        assert l.min_value == 1.0
        assert l.max_value == 10.0
        assert l.unit == "m"
        assert l.replicates == 3
        assert l.standard_deviation == "bad value"

