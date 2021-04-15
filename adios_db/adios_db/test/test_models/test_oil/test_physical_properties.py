import pytest

from adios_db.models.common.measurement import Temperature, Density

from adios_db.models.oil.physical_properties import (PhysicalProperties,
                                                     DensityPoint,
                                                     DensityList,
                                                     InterfacialTensionList,
                                                     DynamicViscosityPoint,
                                                     DynamicViscosityList,
                                                     KinematicViscosityPoint,
                                                     KinematicViscosityList,)


class TestDensityPoint:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = DensityPoint()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = DensityPoint.from_py_json({})

    def test_from_json(self):
        json_obj = {'density': {'value': 900.0, 'unit': 'kg/m^3',
                                'standard_deviation': 1.2, 'replicates': 3},
                    'ref_temp': {'value': 273.15, 'unit': 'K',
                                 'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = DensityPoint.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['density']['unit_type'] = 'density'
        json_obj['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestDensityList:
    def test_init_empty(self):
        assert DensityList().py_json() == []

    def test_from_json_empty(self):
        assert DensityList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'density': {'value': 900.0, 'unit': 'kg/m^3',
                                 'standard_deviation': 1.2, 'replicates': 3},
                     'ref_temp': {'value': 273.15, 'unit': 'K',
                                  'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = DensityList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['density']['unit_type'] = 'density'
        json_obj[0]['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj

    def test_validate_duplicate_values(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'),
                           )
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0.001, unit='C'),
                           )

        DL = DensityList((dp1, dp2))

        msgs = DL.validate()

        print(msgs)

        assert len(msgs) == 1
        assert "E050:" in msgs[0]

    def test_validate_no_duplicate_values(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'),
                           )
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=15, unit='C'),
                           )

        DL = DensityList((dp1, dp2))

        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 0

    def test_validate_no_values(self):
        """
        it shouldn't crash with no data!
        """
        DL = DensityList()

        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 0

    def test_validate_one_value(self):
        """
        it shouldn't crash (or give an warning) with one value!
        """
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'),
                           )

        DL = DensityList((dp1,))

        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 0


    def test_validate_bad_temp(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='K'),
                           )
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=20.0, unit='K'),
                           )

        DL = DensityList((dp1, dp2))

        msgs = DL.validate()

        print(msgs)

        assert len(msgs) == 2
        for msg in msgs:
            assert "E040:" in msg
            assert "Density" in msg


class TestDynamicViscosityPoint:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = DynamicViscosityPoint()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = DynamicViscosityPoint.from_py_json({})

    def test_from_json(self):
        json_obj = {'viscosity': {'value': 100.0, 'unit': 'cP',
                                  'standard_deviation': 1.2, 'replicates': 3},
                    'ref_temp': {'value': 273.15, 'unit': 'K',
                                 'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = DynamicViscosityPoint.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['viscosity']['unit_type'] = 'dynamicviscosity'
        json_obj['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestDynamicViscosityList:
    def test_init_empty(self):
        assert DynamicViscosityList().py_json() == []

    def test_from_json_empty(self):
        assert DynamicViscosityList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'viscosity': {'value': 100.0, 'unit': 'cP',
                                   'standard_deviation': 1.2, 'replicates': 3},
                     'ref_temp': {'value': 273.15, 'unit': 'K',
                                  'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = DynamicViscosityList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['viscosity']['unit_type'] = 'dynamicviscosity'
        json_obj[0]['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestKinematicViscosityPoint:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = KinematicViscosityPoint()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = KinematicViscosityPoint.from_py_json({})

    def test_from_json(self):
        json_obj = {'viscosity': {'value': 100.0, 'unit': 'cSt',
                                  'standard_deviation': 1.2, 'replicates': 3},
                    'ref_temp': {'value': 273.15, 'unit': 'K',
                                 'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = KinematicViscosityPoint.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['viscosity']['unit_type'] = 'kinematicviscosity'
        json_obj['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestKinematicViscosityList:
    def test_init_empty(self):
        assert KinematicViscosityList().py_json() == []

    def test_from_json_empty(self):
        assert KinematicViscosityList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'viscosity': {'value': 100.0, 'unit': 'cSt',
                                   'standard_deviation': 1.2, 'replicates': 3},
                     'ref_temp': {'value': 273.15, 'unit': 'K',
                                  'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = KinematicViscosityList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['viscosity']['unit_type'] = 'kinematicviscosity'
        json_obj[0]['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestPhysicalProperties:
    def test_init(self):
        s = PhysicalProperties()

        for attr in ('pour_point',
                     'flash_point',
                     'densities',
                     'kinematic_viscosities',
                     'dynamic_viscosities',
                     'interfacial_tension_air',
                     'interfacial_tension_water',
                     'interfacial_tension_seawater'):
            assert hasattr(s, attr)

        assert type(s.densities) == DensityList
        assert type(s.kinematic_viscosities) == KinematicViscosityList
        assert type(s.dynamic_viscosities) == DynamicViscosityList
        assert type(s.interfacial_tension_air) == InterfacialTensionList
        assert type(s.interfacial_tension_water) == InterfacialTensionList
        assert type(s.interfacial_tension_seawater) == InterfacialTensionList

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
                                       'interfacial_tension_air',
                                       'interfacial_tension_water',
                                       'interfacial_tension_seawater'}

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
