import pytest

from adios_db.models.oil.properties import (DistCut,
                                            DistCutList,
                                            Distillation,
                                            InterfacialTensionPoint,
                                            InterfacialTensionList,
                                            Dispersibility,
                                            DispersibilityList,
                                            Emulsion,
                                            EmulsionList)
from adios_db.models.common.measurement import (Temperature,
                                                MassFraction,
                                                )


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
    # note: this is over-testing, the "*List" objects are already tested
    #       so if anything changes, better to remove most of these tests
    #       than keep fixing them.
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

def make_dist_cut_list(data, temp_unit='K'):

    cuts = [DistCut(fraction=MassFraction(value=f, unit="fraction"),
                    vapor_temp=Temperature(value=t, unit=temp_unit))
            for f, t in data]
    return DistCutList(cuts)


class TestDistillation:
    """
    tests for the higher level distillation object
    """
    data = ((.05, 16.42),
            (.10, 37.11),
            (.20, 68.79),
            (.30, 90.6),
            (.40, 112.47),
            (.50, 136.94),
            (.60, 172.51),
            (.70, 218.88),
            (.80, 279.8),
            (.90, 368.2),
            (.95, 445.61),
            )

    @staticmethod
    def make_dist_cut_list(data, temp_unit='K'):

        cuts = [DistCut(fraction=MassFraction(value=f, unit="fraction"),
                        vapor_temp=Temperature(value=t, unit=temp_unit))
                for f, t in data]
        return DistCutList(cuts)

    def test_distillation(self):
        dist = Distillation(type="mass fraction",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_included=MassFraction(value=0.8, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
                            )

        # few random things
        assert len(dist.cuts) == 11
        assert dist.cuts[3].fraction.value == 0.3
        assert dist.cuts[3].vapor_temp.value == 90.6

        assert dist.fraction_included == MassFraction(0.8, unit="fraction")

    # need to test validation!


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
