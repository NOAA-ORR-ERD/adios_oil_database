import pytest

from oil_database.models.common.measurement import Temperature, Density

from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList)

from oil_database.models.oil.sample import Sample, SampleList
from oil_database.models.oil.physical_properties import PhysicalProperties


class TestSample:
    def test_init(self):
        s = Sample()

        for attr in ('name', 'short_name',
                     'fraction_weathered',
                     'boiling_point_range',
                     'cut_volume',
                     'physical_properties',
                     'environmental_behavior',
                     'compounds',
                     'bulk_composition',
                     'distillation_data',
                     'SARA',
                     'CCME',
                     'headspace_analysis',
                     'miscellaneous',
                     'extra_data'):
            assert hasattr(s, attr)

        assert s.name == "Fresh Oil Sample"
        assert s.short_name == "Fresh Oil"

    def test_json(self):
        s = Sample(short_name="short",
                   name="a longer name that is more descriptive")
        py_json = s.py_json()  # the sparse version

        assert tuple(py_json.keys()) == ('name', 'short_name')

    def test_json_non_sparse(self):
        s = Sample()
        py_json = s.py_json(sparse=False)

        for attr in ('name', 'short_name',
                     'fraction_weathered',
                     'boiling_point_range',
                     'cut_volume',
                     'physical_properties',
                     'environmental_behavior',
                     'compounds',
                     'bulk_composition',
                     'distillation_data',
                     'SARA',
                     'CCME',
                     'headspace_analysis',
                     'miscellaneous',
                     'extra_data'):
            assert attr in py_json

        assert py_json['name'] == "Fresh Oil Sample"
        assert py_json['short_name'] == "Fresh Oil"

    def test_add_non_existing(self):
        s = Sample(short_name="short",
                   name="a longer name that is more descriptive")

        with pytest.raises(AttributeError):
            s.something_random = 43

    def test_complete_sample(self):
        """
        trying to do a pretty complete one

        Note: This is more an integration test.  Each complex attribute of the
              Sample should have its own pytests
        """
        s = Sample(short_name="short",
                   name="a longer name that is more descriptive")
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

        py_json = s.py_json(sparse=False)  # the non-sparse version

        for name in ('fraction_weathered',
                     'boiling_point_range',
                     'physical_properties'):
            assert name in py_json

        assert py_json['name'] == "a longer name that is more descriptive"
        assert py_json['short_name'] == "short"

        for name in ('densities',
                     'kinematic_viscosities',
                     'dynamic_viscosities'):
            assert name in py_json['physical_properties']

        # Now test some real stuff:
        dens = py_json['physical_properties']['densities']
        print(type(dens))

        assert type(dens) == list
        assert dens[0]['density']['value'] == 0.8751


class TestSampleList:
    def test_empty(self):
        sl = SampleList()

        assert len(sl) == 0

    def test_populated(self):
        s = Sample()
        sl = SampleList([s])

        assert len(sl) == 1
        assert type(sl[0]) == Sample
