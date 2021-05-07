import pytest

from adios_db.models.oil.distillation import (DistCut,
                                              DistCutList,
                                              Distillation,
                                              )
from adios_db.models.common.measurement import (Temperature,
                                                Concentration,
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
        json_obj['fraction']['unit_type'] = 'concentration'
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
        json_obj[0]['fraction']['unit_type'] = 'concentration'
        json_obj[0]['vapor_temp']['unit_type'] = 'temperature'

        assert model.py_json() == json_obj

def make_dist_cut_list(data, temp_unit='K'):

    cuts = [DistCut(fraction=Concentration(value=f, unit="fraction"),
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

        cuts = [DistCut(fraction=Concentration(value=f, unit="fraction"),
                        vapor_temp=Temperature(value=t, unit=temp_unit))
                for f, t in data]
        return DistCutList(cuts)

    def test_distillation(self):
        dist = Distillation(type="mass fraction",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_recovered=Concentration(value=0.8, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
                            )

        # few random things
        assert len(dist.cuts) == 11
        assert dist.cuts[3].fraction.value == 0.3
        assert dist.cuts[3].vapor_temp.value == 90.6

        assert dist.fraction_recovered == Concentration(0.8, unit="fraction")

        msgs = dist.validate()
        assert msgs == []

    def test_validation_bad_temps(self):
        dist = Distillation(type="mass fraction",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_recovered=Concentration(value=0.8, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='K')
                            )
        msgs = dist.validate()

        print(msgs)
        # make sure there is something there!
        assert msgs

        errs = sum(1 for e in msgs if 'E040:' in e)
        assert errs == 7


    def test_validation_bad_fraction(self):
        dist = Distillation(type="mass fraction",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_recovered=Concentration(value=0.8, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
                            )
        dist.cuts[2].fraction.value = 1.1
        dist.cuts[4].fraction.value = -0.9

        msgs = dist.validate()

        errs = sum(1 for e in msgs if 'E041:' in e)
        assert errs == 2

    def test_validation_bad_type(self):
        dist = Distillation(type="mass fractions",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_recovered=Concentration(value=0.8, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
                            )
        msgs = dist.validate()

        # make sure there is something there!
        assert len(msgs) == 1
        assert "E032:" in msgs[0]

    def test_validation_bad_fraction_recovered(self):
        dist = Distillation(type="mass fraction",
                            method="some arbitrary method",
                            end_point=Temperature(value=15, unit="C"),
                            fraction_recovered=Concentration(value=1.1, unit="fraction"),
                            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
                            )
        msgs = dist.validate()

        # make sure there is something there!
        assert len(msgs) == 1
        assert "E041: Value for distillation fraction recovered: 1.1" in msgs[0]

