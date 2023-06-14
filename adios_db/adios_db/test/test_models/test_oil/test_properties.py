import pytest

from adios_db.models.oil.properties import (InterfacialTensionPoint,
                                            InterfacialTensionList,
                                            Dispersibility,
                                            DispersibilityList,
                                            Emulsion,
                                            EmulsionList)
from adios_db.models.oil.physical_properties import (DynamicViscosityPoint,
                                                     KinematicViscosityPoint)
from adios_db.models.common.measurement import (Temperature,
                                                AngularVelocity,
                                                MassFraction,
                                                DynamicViscosity,
                                                KinematicViscosity)


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
        model = Dispersibility()

        assert model.dispersant is None
        assert model.effectiveness is None
        assert model.method is None

    def test_from_json_empty(self):
        model = Dispersibility.from_py_json({})

        assert model.dispersant is None
        assert model.effectiveness is None
        assert model.method is None

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
        """
        this should work, if useless
        """
        model = Emulsion()

        assert model.age is None
        assert model.complex_modulus is None
        # and the rest, but how much can you test?

    def test_from_json_empty(self):

        model = Emulsion.from_py_json({})

        assert model == Emulsion()

    def test_from_json(self):
        json_obj = {
            'age': {'value': 0.0, 'unit': 'day', 'unit_type': 'time'},
            'complex_modulus': {'value': 1.0, 'unit': 'Pa',
                                'standard_deviation': 1.2,
                                'replicates': 3},
            'storage_modulus': {'value': 1.0, 'unit': 'Pa',
                                'standard_deviation': 1.2,
                                'replicates': 3},
            'loss_modulus': {'value': 1.0, 'unit': 'Pa',
                             'standard_deviation': 1.2,
                             'replicates': 3},
            'tan_delta_v_e': {'value': 10.0,
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

        assert model.complex_modulus.unit_type == "pressure"
        assert model.complex_modulus.value == 1.0
        assert model.complex_modulus.unit == "Pa"

        assert model.age.value == 0.0

        assert model.storage_modulus.standard_deviation == 1.2

        assert model.loss_modulus.replicates == 3
        assert model.tan_delta_v_e.value == 10.0
        assert model.complex_viscosity.unit == 'cP'
        assert model.water_content.unit_type == 'massfraction'

    def test_from_partial_json(self):
        """
        Should be able to load an incomplete object
        """
        json_obj = {
            'water_content': {'value': 10.0, 'unit': '%',
                              'standard_deviation': 1.2,
                              'replicates': 3},
        }

        model = Emulsion.from_py_json(json_obj)

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj['water_content']['unit_type'] = 'massfraction'

        # this works, because py_json is sparse by default
        assert model.py_json() == json_obj

    def test_from_partial_with_dynamic_viscosity(self):
        """
        Should be able to load an incomplete object
        """
        model = Emulsion()
        model.dynamic_viscosities.append(
            DynamicViscosityPoint(viscosity=DynamicViscosity(value=660000,
                                                             unit='cP'),
                                  ref_temp=Temperature(value=15, unit='C'),
                                  shear_rate=AngularVelocity(1, '1/s'),
                                  ))
        model.water_content = MassFraction(value=80.0, unit='%')

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj = model.py_json()
        print(json_obj)

        # completely arbitrary single value to check
        assert json_obj['dynamic_viscosities'][0]['ref_temp']['value'] == 15
        assert Emulsion.from_py_json(json_obj) == model

    def test_from_partial_with_kinematic_viscosity(self):
        """
        Should be able to load an incomplete object
        """
        model = Emulsion()
        model.kinematic_viscosities.append(KinematicViscosityPoint(
            viscosity=KinematicViscosity(value=660000, unit='cSt'),
            ref_temp=Temperature(value=15, unit='C'),
            shear_rate=AngularVelocity(1, '1/s'),
        ))
        model.water_content = MassFraction(value=80.0, unit='%')

        # the measurement classes will add unit_type, so we add it to more
        # easily compare the output
        json_obj = model.py_json()
        print(json_obj)

        # completely arbitrary single value to check
        assert json_obj['kinematic_viscosities'][0]['ref_temp']['value'] == 15
        assert Emulsion.from_py_json(json_obj) == model


class TestEmulsionList:
    # NOTE: this is redundant testing from above!
    def test_init_empty(self):
        assert EmulsionList().py_json() == []

    def test_from_json_empty(self):
        assert EmulsionList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{
            'age': {'value': 0.0, 'unit': 'day', 'unit_type': 'time'},
            'complex_modulus': {'value': 1.0, 'unit': 'Pa',
                                'standard_deviation': 1.2,
                                'replicates': 3},
            'storage_modulus': {'value': 1.0, 'unit': 'Pa',
                                'standard_deviation': 1.2,
                                'replicates': 3},
            'loss_modulus': {'value': 1.0, 'unit': 'Pa',
                             'standard_deviation': 1.2,
                             'replicates': 3},
            'tan_delta_v_e': {'value': 10.0,
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
        json_obj[0]['complex_modulus']['unit_type'] = "pressure"
        json_obj[0]['storage_modulus']['unit_type'] = "pressure"
        json_obj[0]['loss_modulus']['unit_type'] = "pressure"
        json_obj[0]['tan_delta_v_e']['unit_type'] = 'unitless'
        json_obj[0]['complex_viscosity']['unit_type'] = 'dynamicviscosity'
        json_obj[0]['water_content']['unit_type'] = 'massfraction'

        assert model.py_json() == json_obj
