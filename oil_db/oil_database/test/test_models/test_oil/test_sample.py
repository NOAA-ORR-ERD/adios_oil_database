import pytest

from oil_database.models.common.measurement import Temperature, Density

from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList)

from oil_database.models.oil.sample import Sample, SampleList
from oil_database.models.oil.metadata import SampleMetaData
from oil_database.models.oil.physical_properties import PhysicalProperties


class TestSample:
    def test_init(self):
        s = Sample()

        for attr in ('CCME',
                     'ESTS_hydrocarbon_fractions',
                     'SARA',
                     'bulk_composition',
                     'compounds',
                     'cut_volume',
                     'distillation_data',
                     'environmental_behavior',
                     'extra_data',
                     'headspace_analysis',
                     'industry_properties',
                     'metadata',
                     'miscellaneous',
                     'physical_properties'):
            assert hasattr(s, attr)

        assert s.metadata.name == "Fresh Oil Sample"
        assert s.metadata.short_name == "Fresh Oil"

    def test_json(self):
        s = Sample(metadata=SampleMetaData(
            short_name="short",
            name="a longer name that is more descriptive"
        ))
        py_json = s.py_json()  # the sparse version

        assert tuple(py_json['metadata'].keys()) == ('name', 'short_name')

    def test_json_non_sparse(self):
        s = Sample()
        py_json = s.py_json(sparse=False)

        for attr in ('CCME',
                     'ESTS_hydrocarbon_fractions',
                     'SARA',
                     'bulk_composition',
                     'compounds',
                     'cut_volume',
                     'distillation_data',
                     'environmental_behavior',
                     'extra_data',
                     'headspace_analysis',
                     'industry_properties',
                     'metadata',
                     'miscellaneous',
                     'physical_properties'):
            assert attr in py_json

        assert py_json['metadata']['name'] == "Fresh Oil Sample"
        assert py_json['metadata']['short_name'] == "Fresh Oil"

    def test_add_non_existing(self):
        s = Sample()

        with pytest.raises(AttributeError):
            s.something_random = 43

    def test_complete_sample(self):
        """
        trying to do a pretty complete one

        Note: This is more an integration test.  Each complex attribute of the
              Sample should have its own pytests
        """
        s = Sample(metadata=SampleMetaData(
            short_name="short",
            name="a longer name that is more descriptive")
        )
        p = PhysicalProperties()

        s.metadata.fraction_weathered = 0.23
        s.metadata.boiling_point_range = None

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

        for name in ('CCME',
                     'ESTS_hydrocarbon_fractions',
                     'SARA',
                     'bulk_composition',
                     'compounds',
                     'cut_volume',
                     'distillation_data',
                     'environmental_behavior',
                     'extra_data',
                     'headspace_analysis',
                     'industry_properties',
                     'metadata',
                     'miscellaneous',
                     'physical_properties'):
            assert name in py_json

        assert py_json['metadata']['name'] == ('a longer name that is more '
                                               'descriptive')
        assert py_json['metadata']['short_name'] == "short"

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
