
import pytest

from oil_database.models.oil.sample import Sample


def test_sample_init():
    s = Sample()

    assert s.name == "Fresh, Unweathered Oil"
    assert s.short_name == "Fresh"


def test_sample_json_sparse():
    s = Sample(short_name="short",
               name="a longer name that is more descriptive",
               )
    py_json = s.py_json()  # the sparse version

    print(py_json)

    assert py_json == {'name': 'a longer name that is more descriptive',
                       'short_name': 'short'}


def test_sample_json_full():
    s = Sample()
    py_json = s.py_json(sparse=False)  # the sparse version

    print(py_json)

    assert py_json['name'] == "Fresh, Unweathered Oil"
    assert py_json['short_name'] == "Fresh"
    for name in ('fraction_weathered',
                 'boiling_point_range',
                 'densities',
                 'kvis',
                 'dvis',
                 ):
        assert name in py_json
