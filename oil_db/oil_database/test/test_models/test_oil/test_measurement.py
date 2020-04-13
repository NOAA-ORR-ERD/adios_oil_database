import pytest

from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList,
                                                 DynamicViscosityPoint,
                                                 DynamicViscosityList,
                                                 KinematicViscosityPoint,
                                                 KinematicViscosityList,
                                                 DistCut,
                                                 DistCutList,
                                                 InterfacialTensionPoint,
                                                 InterfacialTensionList,
                                                 Dispersibility,
                                                 DispersibilityList,
                                                 Emulsion,
                                                 EmulsionList)


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


class TestDistCut:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = DistCut()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = DistCut.from_py_json({})

    def test_from_json(self):
        json_obj = {'fraction': {'value': 10.0, 'unit': '%',
                                 'standard_deviation': 1.2, 'replicates': 3},
                    'vapor_temp': {'value': 273.15, 'unit': 'K',
                                   'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = DistCut.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['fraction']['unit_type'] = 'massfraction'
        json_obj['vapor_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestDistCutList:
    def test_init_empty(self):
        assert DistCutList().py_json() == []

    def test_from_json_empty(self):
        assert DistCutList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'fraction': {'value': 10.0, 'unit': '%',
                                  'standard_deviation': 1.2, 'replicates': 3},
                     'vapor_temp': {'value': 273.15, 'unit': 'K',
                                    'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = DistCutList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['fraction']['unit_type'] = 'massfraction'
        json_obj[0]['vapor_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestInterfacialTensionPoint:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = InterfacialTensionPoint()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = InterfacialTensionPoint.from_py_json({})

    def test_from_json(self):
        json_obj = {'interface': 'water',
                    'tension': {'value': 1000.0, 'unit': 'dyne/cm',
                                'standard_deviation': 1.2, 'replicates': 3},
                    'ref_temp': {'value': 273.15, 'unit': 'K',
                                 'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = InterfacialTensionPoint.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['tension']['unit_type'] = 'interfacialtension'
        json_obj['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestInterfacialTensionList:
    def test_init_empty(self):
        assert InterfacialTensionList().py_json() == []

    def test_from_json_empty(self):
        assert InterfacialTensionList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'interface': 'water',
                     'tension': {'value': 1000.0, 'unit': 'dyne/cm',
                                 'standard_deviation': 1.2, 'replicates': 3},
                     'ref_temp': {'value': 273.15, 'unit': 'K',
                                  'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = InterfacialTensionList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['tension']['unit_type'] = 'interfacialtension'
        json_obj[0]['ref_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj


class TestDispersibility:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = Dispersibility()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = Dispersibility.from_py_json({})

    def test_from_json(self):
        json_obj = {'dispersant': 'corexit',
                    'effectiveness': {'value': 10.0, 'unit': '%',
                                      'standard_deviation': 1.2,
                                      'replicates': 3},
                    }
        model = Dispersibility.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['effectiveness']['unit_type'] = 'massfraction'

        assert model.py_json() == json_obj


class TestDispersibilityList:
    def test_init_empty(self):
        assert DispersibilityList().py_json() == []

    def test_from_json_empty(self):
        assert DispersibilityList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'dispersant': 'corexit',
                     'effectiveness': {'value': 10.0, 'unit': '%',
                                       'standard_deviation': 1.2,
                                       'replicates': 3},
                     }]
        model = DispersibilityList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['effectiveness']['unit_type'] = 'massfraction'

        assert model.py_json() == json_obj


class TestEmulsion:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = Emulsion()

    def test_from_json_empty(self):
        with pytest.raises(TypeError):
            _model = Emulsion.from_py_json({})

    def test_from_json(self):
        json_obj = {'age': {'value': 0.0, 'unit': 'day', 'unit_type': 'time'},
                    'complex_modulus': {'value': 1.0, 'unit': 'Pa',
                                        'standard_deviation': 1.2,
                                        'replicates': 3},
                    'storage_modulus': {'value': 1.0, 'unit': 'Pa',
                                        'standard_deviation': 1.2,
                                        'replicates': 3},
                    'loss_modulus': {'value': 1.0, 'unit': 'Pa',
                                     'standard_deviation': 1.2,
                                     'replicates': 3},
                    'tan_delta': {'value': 10.0, 'unit': '%',
                                  'standard_deviation': 1.2,
                                  'replicates': 3},
                    'complex_viscosity': {'value': 100.0, 'unit': 'cP',
                                          'standard_deviation': 1.2,
                                          'replicates': 3},
                    'water_content': {'value': 10.0, 'unit': '%',
                                      'standard_deviation': 1.2,
                                      'replicates': 3},
                    }
        model = Emulsion.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['complex_modulus']['unit_type'] = 'adhesion'
        json_obj['storage_modulus']['unit_type'] = 'adhesion'
        json_obj['loss_modulus']['unit_type'] = 'adhesion'
        json_obj['tan_delta']['unit_type'] = 'massfraction'
        json_obj['complex_viscosity']['unit_type'] = 'dynamicviscosity'
        json_obj['water_content']['unit_type'] = 'massfraction'

        assert model.py_json() == json_obj


class TestEmulsionList:
    def test_init_empty(self):
        assert EmulsionList().py_json() == []

    def test_from_json_empty(self):
        assert EmulsionList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'age': {'value': 0.0, 'unit': 'day', 'unit_type': 'time'},
                     'complex_modulus': {'value': 1.0, 'unit': 'Pa',
                                         'standard_deviation': 1.2,
                                         'replicates': 3},
                     'storage_modulus': {'value': 1.0, 'unit': 'Pa',
                                         'standard_deviation': 1.2,
                                         'replicates': 3},
                     'loss_modulus': {'value': 1.0, 'unit': 'Pa',
                                      'standard_deviation': 1.2,
                                      'replicates': 3},
                     'tan_delta': {'value': 10.0, 'unit': '%',
                                   'standard_deviation': 1.2,
                                   'replicates': 3},
                     'complex_viscosity': {'value': 100.0, 'unit': 'cP',
                                           'standard_deviation': 1.2,
                                           'replicates': 3},
                     'water_content': {'value': 10.0, 'unit': '%',
                                       'standard_deviation': 1.2,
                                       'replicates': 3},
                     }]
        model = EmulsionList.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj[0]['complex_modulus']['unit_type'] = 'adhesion'
        json_obj[0]['storage_modulus']['unit_type'] = 'adhesion'
        json_obj[0]['loss_modulus']['unit_type'] = 'adhesion'
        json_obj[0]['tan_delta']['unit_type'] = 'massfraction'
        json_obj[0]['complex_viscosity']['unit_type'] = 'dynamicviscosity'
        json_obj[0]['water_content']['unit_type'] = 'massfraction'

        assert model.py_json() == json_obj
