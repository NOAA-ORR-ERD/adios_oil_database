
import pytest

from oil_database.models.oil.sample import Sample
from oil_database.models.oil.values import (Density, Viscosity, UnittedValue)


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

    assert tuple(py_json.keys()) == ('name', 'short_name')


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

def test_complete_sample():
    """
    trying to do a pretty complete one
    """
    s = Sample(short_name="short",
               name="a longer name that is more descriptive",
               )
    s.fraction_weathered = 0.23
    s.boiling_point_range = None
    s.densities = [Density(standard_deviation=1.2,
                           replicates=3,
                           density=UnittedValue(0.8751, "kg/m^3"),
                           ref_temp=UnittedValue(15.0, "C"),
                           ),
                   Density(standard_deviation=1.4,
                           replicates=5,
                           density=UnittedValue(0.99, "kg/m^3"),
                           ref_temp=UnittedValue(25.0, "C"),
                           ),
                   ]




