import pytest

from oil_database.models.common.measurement import Temperature, Density

from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList,
                                                 KinematicViscosityList,
                                                 DynamicViscosityList,
                                                 InterfacialTensionList)

from oil_database.models.oil.physical_properties import PhysicalProperties


class TestPhysicalProperties:
    def test_init(self):
        s = PhysicalProperties()

        for attr in ('pour_point',
                     'flash_point',
                     'densities',
                     'kinematic_viscosities',
                     'dynamic_viscosities',
                     'interfacial_tensions'):
            assert hasattr(s, attr)

        assert type(s.densities) == DensityList
        assert type(s.kinematic_viscosities) == KinematicViscosityList
        assert type(s.dynamic_viscosities) == DynamicViscosityList
        assert type(s.interfacial_tensions) == InterfacialTensionList

    def test_json(self):
        s = PhysicalProperties()
        py_json = s.py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_non_sparse(self):
        s = PhysicalProperties()
        py_json = s.py_json(sparse=False)

        assert set(py_json.keys()) == {'pour_point',
                                       'flash_point',
                                       'densities',
                                       'kinematic_viscosities',
                                       'dynamic_viscosities',
                                       'interfacial_tensions'}

    def test_add_non_existing(self):
        s = PhysicalProperties()

        with pytest.raises(AttributeError):
            s.something_random = 43

    def test_complete_sample(self):
        """
        trying to do a pretty complete one

        Note: This is more an integration test.  Each complex attribute of the
              PhysicalProperties dataclass should have its own pytests
        """
        p = PhysicalProperties()

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

        py_json = p.py_json(sparse=False)  # the non-sparse version

        for name in ('densities',
                     'kinematic_viscosities',
                     'dynamic_viscosities'):
            assert name in py_json

        # Now test some real stuff:
        dens = py_json['densities']
        print(type(dens))

        assert type(dens) == list
        assert dens[0]['density']['value'] == 0.8751
