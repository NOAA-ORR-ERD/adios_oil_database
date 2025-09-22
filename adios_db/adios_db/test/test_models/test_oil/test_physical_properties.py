import pytest

from adios_db.models.common.measurement import Temperature, Density

from adios_db.models.oil.physical_properties import (PhysicalProperties,
                                                     DensityPoint,
                                                     DensityList,
                                                     InterfacialTension,
                                                     InterfacialTensionPoint,
                                                     InterfacialTensionList,
                                                     DynamicViscosityPoint,
                                                     DynamicViscosityList,
                                                     KinematicViscosity,
                                                     KinematicViscosityPoint,
                                                     KinematicViscosityList)


class TestDensityPoint:
    def test_init_empty(self):
        model = DensityPoint()

        assert model.density is None
        assert model.ref_temp is None
        assert model.method is None

    def test_from_json_empty(self):
        model = DensityPoint.from_py_json({})

        assert model.density is None
        assert model.ref_temp is None
        assert model.method is None

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


class TestRefTempList_delete_empty_values:
    """
    most of this is tested through the subclasses, but seems better to put key stuff here.
    """
    def get_new_list(self):
        """
        using densities, but should work for most things
        """
        densities = DensityList([
            DensityPoint(density=Density(value=0.8751, unit="g/cm^3"),
                         ref_temp=Temperature(value=60.0, unit="F")),
            DensityPoint(density=Density(value=0.99, unit="g/cm^3"),
                         ref_temp=Temperature(value=25.0, unit="C")),
            DensityPoint(density=Density(value=0.96, unit="g/cm^3"),
                         ref_temp=Temperature(value=50.0, unit="C")),

        ])
        return densities

    def test_remove_empty_all_good(self):
        """
        list is full -- nothing should get removed
        """
        dl = self.get_new_list()

        dl.delete_empty_values()

        assert dl == self.get_new_list()

    def test_remove_empty_some_none(self):
        """
        Set some to None
        """
        orig = self.get_new_list()
        dl = self.get_new_list()

        dl[0].ref_temp = None
        dl[2].density = None

        dl.delete_empty_values()

        assert dl[0] == orig[1]
        assert len(dl) == 1

    def test_remove_empty_some_empty(self):
        """
        Set some to None
        """
        orig = self.get_new_list()
        dl = self.get_new_list()

        # set a couple to empty
        dl[0].ref_temp = Temperature(unit="C")
        dl[2].density = Density(unit="g/cm^3")

        assert dl[0].ref_temp.is_empty()
        assert dl[2].density.is_empty()

        dl.delete_empty_values()

        assert dl[0] == orig[1]
        assert len(dl) == 1


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

    def test_from_data(self):
        """
        simple creation from a data table
        """
        data = [(0.8663, "g/cm³", 15, "C"),
                (0.9012, "g/cm³", 0.0, "C"),
                ]
        dl = DensityList.from_data(data)

        pjs = dl.py_json()

        assert pjs == [{'density': {'value': 0.9012, 'unit': 'g/cm³', 'unit_type': 'density'},
                        'ref_temp': {'value': 0.0, 'unit': 'C', 'unit_type': 'temperature'}},
                       {'density': {'value': 0.8663, 'unit': 'g/cm³', 'unit_type': 'density'},
                        'ref_temp': {'value': 15.0, 'unit': 'C', 'unit_type': 'temperature'}},
                       ]





    def test_validate_duplicate_values(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'))
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0.001, unit='C'))

        DL = DensityList((dp1, dp2))

        msgs = DL.validate()

        print(msgs)

        assert len(msgs) == 1
        assert "E050:" in msgs[0]

    def test_validate_no_duplicate_values(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'))
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=15, unit='C'))

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
                           ref_temp=Temperature(value=0, unit='C'))

        DL = DensityList((dp1,))
        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 0

    def test_validate_bad_temp(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='K'))
        dp2 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=20.0, unit='K'))

        DL = DensityList((dp1, dp2))
        msgs = DL.validate()

        for msg in msgs:
            print(msg)

        assert len(msgs) == 4
        for msg in msgs:
            assert ("E040:" in msg and "DensityList" in msg
                    or
                    "W010:" in msg and "Temperature" in msg
                    )

    def test_validate_non_numeric_value(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'))
        dp2 = DensityPoint(density=Density(value="NM", unit='kg/m^3'),
                           ref_temp=Temperature(value=15, unit='C'))

        DL = DensityList((dp1, dp2))
        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 2
        for msg in msgs:
           assert ("E048:" in msg) or ("E044:" in msg)

    def test_validate_negative_numeric_value(self):
        dp1 = DensityPoint(density=Density(value=900, unit='kg/m^3'),
                           ref_temp=Temperature(value=0, unit='C'))
        dp2 = DensityPoint(density=Density(value="0.0", unit='kg/m^3'),
                           ref_temp=Temperature(value=15, unit='C'))
        dp3 = DensityPoint(density=Density(value="-10.0", unit='kg/m^3'),
                           ref_temp=Temperature(value=15, unit='C'))

        DL = DensityList((dp1, dp2, dp3))
        msgs = DL.validate()

        print(msgs)
        assert len(msgs) == 2
        assert "E044:" in msgs[0]
        assert "0.0" in msgs[0]
        assert "E044:" in msgs[1]
        assert "-10.0" in msgs[1]


class TestDynamicViscosityPoint:
    def test_init_empty(self):
        model = DynamicViscosityPoint()

        assert model.viscosity is None
        assert model.ref_temp is None
        assert model.shear_rate is None
        assert model.method is None

    def test_from_json_empty(self):
        model = DynamicViscosityPoint.from_py_json({})

        assert model.viscosity is None
        assert model.ref_temp is None
        assert model.shear_rate is None
        assert model.method is None

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

    def test_from_data(self):
        """
        simple creation from a data table
        """
        data = [(1234.3, "cP", 273.15, "K"),
                (800.3, "cP", 15.0, "C"),
                ]
        dl = DynamicViscosityList.from_data(data)

        pjs = dl.py_json()

        for p in pjs:
            print(p)

        assert pjs == [{'viscosity': {'value': 1234.3, 'unit': 'cP', 'unit_type': 'dynamicviscosity'},
                        'ref_temp': {'value': 273.15, 'unit': 'K', 'unit_type': 'temperature'}},
                       {'viscosity': {'value': 800.3, 'unit': 'cP', 'unit_type': 'dynamicviscosity'},
                        'ref_temp': {'value': 15.0, 'unit': 'C', 'unit_type': 'temperature'}},
                       ]
    def test_validate_missing_value(self):
        data = [(1234.3, "cP", 273.15, "K"),
                (800.3, "cP", 15.0, "C"),
                ]
        dl = DynamicViscosityList.from_data(data)
        # set one value to None
        dl[0].viscosity.value=None
        print(dl.py_json())

        msgs = dl.validate()

        print(msgs)

        assert len(msgs) == 1
        assert msgs[0] == "E049: Missing value for DynamicViscosity with reference temperature: 273.15"

    def test_validate_all_same(self):
        # from AD02151 "GASOLINE (LEADED)
        data = [{
            "viscosity": {
                "value": 0.001,
                "unit": "kg/(m s)",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 0.0,
                "unit": "C",
                "unit_type": "temperature"
            }
        }, {
            "viscosity": {
                "value": 0.001,
                "unit": "kg/(m s)",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 5.0,
                "unit": "C",
                "unit_type": "temperature"
            }
        }, {
            "viscosity": {
                "value": 0.001,
                "unit": "kg/(m s)",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 15.0,
                "unit": "C",
                "unit_type": "temperature"
            }
        }, {
            "viscosity": {
                "value": 0.001,
                "unit": "kg/(m s)",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 20.0,
                "unit": "C",
                "unit_type": "temperature"
            }
        }]

        dvl = DynamicViscosityList.from_py_json(data)

        msgs = dvl.validate()

        print(msgs)

        assert len(msgs) == 1
        assert "E062:" in msgs[0]


    def test_missing_shear_rate(self):
        data = [{
            "viscosity": {
                "value": 63180.0,
                "unit": "mPas",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 0.0,
                "unit": "C",
                "unit_type": "temperature"
            },
            "shear_rate": {
                "value": 10.0,
                "unit": "1/s",
                "unit_type": "angularvelocity"
            }
        }, {
            "viscosity": {
                "value": 76000.0,
                "unit": "mPas",
                "unit_type": "dynamicviscosity"
            },
            "ref_temp": {
                "value": 15.0,
                "unit": "C",
                "unit_type": "temperature"
            }
        }]

        dvl = DynamicViscosityList.from_py_json(data)

        msgs = dvl.validate()

        print(msgs)

        assert len(msgs) == 1
        assert "W015:" in msgs[0]


class TestKinematicViscosityPoint:
    def test_init_empty(self):
        model = KinematicViscosityPoint()

        assert model.viscosity is None
        assert model.ref_temp is None
        assert model.shear_rate is None
        assert model.method is None

    def test_from_json_empty(self):
        model = KinematicViscosityPoint.from_py_json({})

        assert model.viscosity is None
        assert model.ref_temp is None
        assert model.shear_rate is None
        assert model.method is None

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

    def test_from_data(self):
        """
        simple creation from a data table
        """
        data = [(100, "cSt", 273.15, "K"),
                (1234.3, "cSt", 15.0, "C"),
                ]
        dl = KinematicViscosityList.from_data(data)

        pjs = dl.py_json()

        for p in pjs:
            print(p)

        assert pjs == [{'viscosity': {'value': 100.0, 'unit': 'cSt', 'unit_type': 'kinematicviscosity'},
                        'ref_temp': {'value': 273.15, 'unit': 'K', 'unit_type': 'temperature'}},
                       {'viscosity': {'value': 1234.3, 'unit': 'cSt', 'unit_type': 'kinematicviscosity'},
                        'ref_temp': {'value': 15.0, 'unit': 'C', 'unit_type': 'temperature'}},
                       ]

    def test_missing_ref_temp(self):
        # this occurs a lot when editing the code in the GUI
        kvp = KinematicViscosityPoint(
            viscosity=KinematicViscosity(1000, unit="Cst")
        )

        kvl = KinematicViscosityList((kvp,))
        msgs = kvl.validate()

        assert "E048:" in msgs[0]
        assert "KinematicViscosity" in msgs[0]

    def test_order_kvis(self):
        data = [(100, "cSt", 0, "C"),
                (200, "cSt", 15.0, "C"),
                ]
        kv = KinematicViscosityList.from_data(data)

        msgs = kv.validate()

        assert "E062:" in msgs[0]
        assert "Viscosity" in msgs[0]

    def test_same_kvis(self):
        data = [(100, "cSt", 0, "C"),
                (100, "cSt", 15.0, "C"),
                ]
        kv = KinematicViscosityList.from_data(data)

        msgs = kv.validate()

        assert "E062:" in msgs[0]
        assert "Viscosity" in msgs[0]

    def test_multiple_shear_rates_not_decreasing(self):
        data =  [
                    {
                        "viscosity": {
                            "value": 1000.0,
                            "unit": "cSt",
                            "standard_deviation": 67000.0,
                            "replicates": 3,
                            "unit_type": "kinematicviscosity"
                        },
                        "ref_temp": {
                            "value": 15.0,
                            "unit": "C",
                            "unit_type": "temperature"
                        },
                        "shear_rate": {
                            "value": 10.0,
                            "unit": "1/s",
                            "unit_type": "angularvelocity"
                        },
                        "method": "ESTS 12.06/x.x/M"
                    },
                    {
                        "viscosity": {
                            "value": 900.0,
                            "unit": "cSt",
                            "standard_deviation": 2233480.0,
                            "replicates": 3,
                            "unit_type": "kinematicviscosity"
                        },
                        "ref_temp": {
                            "value": 0.0,
                            "unit": "C",
                            "unit_type": "temperature"
                        },
                        "shear_rate": {
                            "value": 1,
                            "unit": "1/s",
                            "unit_type": "angularvelocity"
                        },
                        "method": "ESTS 12.06/x.x/M"
                    }
                ]
        kvl = KinematicViscosityList.from_py_json(data)

        msgs = kvl.validate()

        print(msgs)

        assert not msgs

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
                                       'appearance',
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


class Test_interfacial_tension:
    # maybe there should be more here?
    def test_missing_ref_temp(self):
        # this was in the actual data -- how?
        # note missing value for temp
        itp = InterfacialTensionPoint(
            tension=InterfacialTension(0.03, unit="N/m"),
            ref_temp=Temperature(unit="K")
        )
        itl = InterfacialTensionList((itp,))
        msgs = itl.validate()

        assert "E048:" in msgs[0]
        assert "InterfacialTension" in msgs[0]

    def test_comment_no_errors(self):
        """
        make sure we can add and save a comment to an InterfacialTensionPoint
        """
        itp = InterfacialTensionPoint(
            tension=InterfacialTension(0.03, unit="N/m"),
            ref_temp=Temperature(value=15.0, unit="C"),
            comment="Too Viscous"
        )
        itl = InterfacialTensionList((itp,))
        msgs = itl.validate()

        assert not msgs

    def test_warning_min_max(self):
        """
        make sure there's a warning if a value has min_value or max_value in it
        """
        itl = InterfacialTensionList([InterfacialTensionPoint(
                                        tension=InterfacialTension(min_value=0.03, unit="N/m"),
                                        ref_temp=Temperature(value=15.0, unit="C"),
                                        comment="Too Viscous"),
                                      InterfacialTensionPoint(
                                        tension=InterfacialTension(0.03, unit="N/m"),
                                        ref_temp=Temperature(value=25.0, unit="C"),
                                        comment="Too Viscous"),
                                      ])

        msgs = itl.validate()
        print(msgs)

        assert len(msgs) == 1
        assert msgs[0] == 'W014: Non-simple value: ">0.03" for InterfacialTensionList'
