
import pytest

from oil_database.models.oil.values import (UnittedValue,
                                            UnittedRange,
                                            )


def test_UnittedValue():
    uv = UnittedValue(1.0, "m")

    assert uv.value == 1.0
    assert uv.unit == "m"


def test_UnittedValue_no_value():
    with pytest.raises(TypeError):
        uv = UnittedValue(1.0)
    with pytest.raises(TypeError):
        uv = UnittedValue("m/s")


def test_UnittedValue_json():
    uv = UnittedValue(1.0, "m")

    py_json = uv.py_json()

    print(py_json)

    assert py_json == {'value': 1.0, 'unit': 'm'}


def test_UnittedValue_from_py_json():
    uv = UnittedValue.from_py_json({'value': 1.0, 'unit': 'm'})

    assert uv.value == 1.0
    assert uv.unit == "m"


def test_UnittedValue_from_py_json_missing_data():

    with pytest.raises(TypeError):
        uv = UnittedValue.from_py_json({'value': 1.0})

    with pytest.raises(TypeError):
        uv = UnittedValue.from_py_json({'unit': 'm/s'})


def test_UnittedRange_both():
    ur = UnittedRange(1.0, 5.0, "ft")

    assert ur.min_value == 1.0
    assert ur.max_value == 5.0
    assert ur.unit == "ft"


def test_UnittedRange_json_sparse():
    ur = UnittedRange(None, 5.0, 'm')

    py_json = ur.py_json()

    assert py_json == {'max_value': 5.0, 'unit': 'm'}


def test_UnittedRange_json_full():
    ur = UnittedRange(None, 5.0, 'm')

    py_json = ur.py_json(sparse=False)

    assert py_json == {'max_value': 5.0,
                       'unit': 'm',
                       'min_value': None}


def test_UnittedRange_from_json():
    ur = UnittedRange.from_py_json({'min_value': 5.0,
                                    'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value is None
    assert ur.unit == "m/s"

