
import pytest

from oil_database.models.common.measurement import Temperature, Density

from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList)

from oil_database.models.oil.sample import Sample
from oil_database.models.oil.physical_properties import PhysicalProperties


def test_sample_init():
    s = Sample()

    assert s.name == "Fresh Oil Sample"
    assert s.short_name == "Fresh Oil"


def test_sample_json_sparse():
    s = Sample(short_name="short",
               name="a longer name that is more descriptive",
               )
    py_json = s.py_json()  # the sparse version

    print(py_json)

    assert tuple(py_json.keys()) == ('name', 'short_name')


def test_sample_add_non_existing():
    s = Sample(short_name="short",
               name="a longer name that is more descriptive",
               )
    with pytest.raises(AttributeError):
        s.something_random = 43


def test_sample_json_full():
    s = Sample()
    py_json = s.py_json(sparse=False)  # the not sparse version

    print(py_json)

    assert py_json['name'] == "Fresh Oil Sample"
    assert py_json['short_name'] == "Fresh Oil"
    for name in ('fraction_weathered',
                 'boiling_point_range',
                 'cut_volume',
                 'physical_properties',
                 'environmental_behavior',
                 'SARA',
                 'distillation_data',
                 'bulk_composition',
                 'compounds',
                 'headspace_analysis',
                 'CCME',
                 'miscellaneous',
                 'extra_data',
                 ):
        assert name in py_json


def test_complete_sample():
    """
    trying to do a pretty complete one
    """
    s = Sample(short_name="short",
               name="a longer name that is more descriptive",
               )
    p = PhysicalProperties()

    s.fraction_weathered = 0.23
    s.boiling_point_range = None

    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="kg/m^3",
                                     standard_deviation=1.2,
                                     replicates=3),
                     ref_temp=Temperature(value=15.0, unit="C")),
        DensityPoint(density=Density(value=0.99, unit="kg/m^3",
                                     standard_deviation=1.4,
                                     replicates=5),
                     ref_temp=Temperature(value=25.0, unit="C"))
    ])

    s.physical_properties = p

    py_json = s.py_json(sparse=False)  # the not sparse version

    print(py_json)

    assert py_json['name'] == "a longer name that is more descriptive"
    assert py_json['short_name'] == "short"
    for name in ('fraction_weathered',
                 'boiling_point_range',
                 'physical_properties',
                 ):
        assert name in py_json

    for name in ('densities',
                 'kinematic_viscosities',
                 'dynamic_viscosities',
                 ):
        assert name in py_json['physical_properties']

    # Now test some real stuff:
    dens = py_json['physical_properties']['densities']
    print(type(dens))

    assert dens[0]['density']['value'] == 0.8751

# def test_sample_from_json():

# now allowing empty sample list
# def test_samplelist():
#     sl = SampleList()
#     assert len(sl) == 1
#     assert type(sl[0]) == Sample
