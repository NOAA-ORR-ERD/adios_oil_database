import pytest

from adios_db.models.oil.properties import (InterfacialTensionPoint,
                                            InterfacialTensionList,
                                            Dispersibility,
                                            DispersibilityList,
                                            Emulsion,
                                            EmulsionList)
from adios_db.models.common.measurement import Temperature


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
        this should work, if uesless
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
        """ Should be able to load an incomplete object """
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
