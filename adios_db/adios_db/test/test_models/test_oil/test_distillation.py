from adios_db.models.oil.distillation import DistCut, DistCutList, Distillation
from adios_db.models.common.measurement import Temperature, Concentration


class TestDistCut:
    def test_init_empty(self):
        """
        empty distillation cut is valid.  We need to support blur editing
        """
        model = DistCut()

        assert model.fraction is None
        assert model.vapor_temp is None

    def test_from_json_empty(self):
        """
        empty distillation cut is valid.  We need to support blur editing
        """
        model = DistCut.from_py_json({})

        assert model.fraction is None
        assert model.vapor_temp is None

    def test_from_json(self):
        json_obj = {'fraction': {'value': 10.0, 'unit': '%',
                                 'unit_type': 'massfraction',
                                 'standard_deviation': 1.2, 'replicates': 3},
                    'vapor_temp': {'value': 273.15, 'unit': 'K',
                                   'unit_type': 'temperature',
                                   'standard_deviation': 1.2, 'replicates': 3}
                    }
        model = DistCut.from_py_json(json_obj)

        assert model.py_json() == json_obj


class TestDistCutList:
    """
    note: this is over-testing, the "*List" objects are already tested
          so if anything changes, better to remove most of these tests
          than keep fixing them.
    """
    def test_init_empty(self):
        assert DistCutList().py_json() == []

    def test_from_json_empty(self):
        assert DistCutList.from_py_json([]).py_json() == []

    def test_from_json(self):
        json_obj = [{'fraction': {'value': 10.0, 'unit': '%',
                                  'unit_type': 'massfraction',
                                  'standard_deviation': 1.2, 'replicates': 3},
                     'vapor_temp': {'value': 273.15, 'unit': 'K',
                                    'unit_type': 'temperature',
                                    'standard_deviation': 1.2, 'replicates': 3}
                     }]
        model = DistCutList.from_py_json(json_obj)

        assert model.py_json() == json_obj


def make_dist_cut_list(data, temp_unit='K'):
    cuts = [DistCut(fraction=Concentration(value=f, unit="fraction"),
                    vapor_temp=Temperature(value=t, unit=temp_unit))
            for f, t in data]

    return DistCutList(cuts)


def test_from_data_arrays():
    """
    see if the constructor from arrays works
    """
    fractions = (1.5, 2.8, 12.4, 23.5, 44.3, 63.9, 82.7, 91.7, 96.2, 98.8)
    frac_unit = 'percent'

    temps = (36.0, 69.0, 119.0, 173.0, 283.0, 391.0, 513.0, 604.0,
             672.0, 729.0)
    temp_unit = 'C'

    dct = DistCutList.from_data_arrays(fractions=fractions,
                                       frac_unit=frac_unit,
                                       temps=temps,
                                       temp_unit=temp_unit)
    assert len(dct) == len(fractions)

    msgs = dct.validate()
    assert not msgs

    assert dct[0].fraction.converted_to('fraction').value == 0.015
    assert dct[0].vapor_temp.converted_to('C').value == 36.0

    assert dct[-1].fraction.converted_to('fraction').value == 0.988
    assert dct[-1].vapor_temp.converted_to('C').value == 729.0


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
        """
        not really needed, now that there is from_data_arrays,

        but keeping this, as the API is different
        """
        fracs, temps = zip(*data)
        return DistCutList.from_data_arrays(fracs, temps,
                                            "fraction", temp_unit)

    def test_distillation(self):
        dist = Distillation(
            type="mass fraction",
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
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=Concentration(value=0.8, unit="fraction"),
            cuts=self.make_dist_cut_list(self.data, temp_unit='K')
        )
        msgs = dist.validate()

        # make sure there is something there!
        print(msgs)
        assert msgs

        errs = sum(1 for e in msgs if 'E040:' in e)
        assert errs == 7

    def test_validation_bad_fraction(self):
        dist = Distillation(
            type="mass fraction",
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
        dist = Distillation(
            type="mass fractions",
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
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=Concentration(value=1.1, unit="fraction"),
            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
        )
        msgs = dist.validate()

        # make sure there is something there!
        assert len(msgs) == 1
        assert "E041: Value for distillation fraction recovered: 1.1" in msgs[0]

    def test_validation_no_fraction_recovered(self):
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=None,
            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
        )
        msgs = dist.validate()

        # make sure there is something there!
        assert len(msgs) == 1
        assert msgs[0].startswith('W009:')

    def test_validation_no_fraction_recovered_no_cuts(self):
        """
        if there is no cut data, it's OK not to have a fraction_recovered
        """
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=None,
        )
        msgs = dist.validate()

        # make sure there is something there!
        assert len(msgs) == 0

    def test_distillation_duplicate_fraction(self):
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=Concentration(value=0.8, unit="fraction"),
            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
        )
        dist.cuts[3].fraction.value = 0.2

        msgs = dist.validate()
        assert len(msgs) == 1
        assert msgs[0].startswith('W013:')

    def test_distillation_accumulative_fraction(self):
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=Concentration(value=0.8, unit="fraction"),
            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
        )
        dist.cuts[5].fraction.value = 0.25

        msgs = dist.validate()
        assert len(msgs) == 1
        assert msgs[0].startswith('E060:')

    def test_distillation_boilingpoints_strictlyincreasing(self):
        dist = Distillation(
            type="mass fraction",
            method="some arbitrary method",
            end_point=Temperature(value=15, unit="C"),
            fraction_recovered=Concentration(value=0.8, unit="fraction"),
            cuts=self.make_dist_cut_list(self.data, temp_unit='C')
        )
        dist.cuts[5].vapor_temp.value = 400.

        msgs = dist.validate()
        assert len(msgs) == 1
        assert msgs[0].startswith('E061:')
