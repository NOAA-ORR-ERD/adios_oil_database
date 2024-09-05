import pytest

from adios_db.models.common.measurement import (Temperature,
                                                Density,
                                                MassFraction)
from adios_db.models.oil.sample import Sample, SampleList
from adios_db.models.oil.metadata import SampleMetaData
from adios_db.models.oil.ccme import CCME
from adios_db.models.oil.physical_properties import (PhysicalProperties,
                                                     DensityPoint,
                                                     DensityList)


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

    @pytest.mark.parametrize("attr", ['CCME',
                                      'SARA',
                                      'bulk_composition',
                                      'compounds',
                                      'distillation_data',
                                      'environmental_behavior',
                                      'extra_data',
                                      'headspace_analysis',
                                      'industry_properties',
                                      'metadata',
                                      'miscellaneous',
                                      'physical_properties'])
    def test_default_empty_attributes(self, attr):
        """
        test that various attributes get a default empty object,
        rather than None
        """
        s = Sample()
        assert getattr(s, attr) is not None

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
            name="a longer name that is more descriptive"
        ))
        p = PhysicalProperties()

        s.metadata.fraction_evaporated = MassFraction(value=11, unit='%')
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


class TestSampleFromJson:
    def test_metadata(self):
        s = Sample.from_py_json({
            'metadata': {
                'name': 'Fresh Oil Sample',
                'short_name': 'Fresh Oil',
                'fraction_evaporated': {
                    'value': 11,
                    'unit': '%',
                    'unit_type': 'massfraction'
                }
            }
        })

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

        assert s.metadata.name == 'Fresh Oil Sample'
        assert s.metadata.short_name == 'Fresh Oil'
        assert s.metadata.fraction_evaporated.value == 11
        assert s.metadata.fraction_evaporated.unit == '%'


def test_sample_with_ccme():
    """
    testing loading a sample with ccme data from py_json
    """
    ccme = CCME()

    ccme.F1 = MassFraction(unit="mg/g", value=15.58)
    ccme.F2 = MassFraction(unit="mg/g", value=50)
    ccme.F3 = MassFraction(unit="mg/g", value=193)
    ccme.F4 = MassFraction(unit="mg/g", value=40)
    ccme.method = "a method name"

    s = Sample(metadata=SampleMetaData(
        short_name="short",
        name="a longer name that is more descriptive"
    ))

    s.metadata.fraction_evaporated = MassFraction(value=16, unit="%")
    s.metadata.boiling_point_range = None
    s.CCME = ccme

    sample_json = s.py_json()

    s2 = Sample.from_py_json(sample_json)

    assert s == s2


class TestSampleList:
    def test_empty(self):
        sl = SampleList()

        assert len(sl) == 0

    def test_populated(self):
        s = Sample()
        sl = SampleList([s])

        assert len(sl) == 1
        assert type(sl[0]) == Sample

    def test_validate_no_repeated_names(self):
        sl = SampleList()

        sl.append(
            Sample(metadata=SampleMetaData(short_name="short",
                                           name="a longer name that is more descriptive")))

        sl.append(
            Sample(metadata=SampleMetaData(short_name="short2",
                                           name="another longer name that is more descriptive")))

        msgs = sl.validate()

        print(msgs)
        for msg in msgs:
            assert "E051" not in msg

    def test_validate_repeated_names(self):
        sl = SampleList()

        sl.append(
            Sample(metadata=SampleMetaData(short_name="short",
                                           name="a longer name that is more descriptive")))

        sl.append(
            Sample(metadata=SampleMetaData(short_name="short",
                                           name="a longer name that is more descriptive")))

        msgs = sl.validate()

        print(msgs)
        found_short_name = False
        found_name = False
        for msg in msgs:
            if "E051" in msg:
                found_short_name = True
            if "E052" in msg:
                found_name = True
        assert found_short_name and found_name

