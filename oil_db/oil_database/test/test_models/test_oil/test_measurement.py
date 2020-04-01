import pytest

from oil_database.models.oil.measurement import (Length,
                                                 Temperature)


#  Note: the Measuremtn base class should not be used on its own
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

    assert py_json == {'value': 1.0, 'unit': 'm'}


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

    assert py_json == {'max_value': 5.0, 'unit': 'm'}


def test_LengthRange_json_full():
    ur = Length(max_value=5.0, unit='m')

    py_json = ur.py_json(sparse=False)

    assert py_json == {'value': None,
                       'max_value': 5.0,
                       'unit': 'm',
                       'min_value': None,
                       'standard_deviation': None,
                       'replicates': None}


def test_LengthRange_from_json():
    ur = Length.from_py_json({'min_value': 5.0,
                                    'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value is None
    assert ur.unit == "m/s"


def test_LengthRange_from_json():
    ur = Length.from_py_json({'min_value': 5.0,
                                    'max_value': 10.1,
                                    'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value == 10.1
    assert ur.unit == "m/s"
