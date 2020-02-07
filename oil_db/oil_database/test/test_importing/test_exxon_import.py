"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""
from pathlib import Path
from pprint import pprint
from math import isclose

import pytest

import unit_conversion as uc

from oil_database.data_sources.exxon_assays import (ExxonDataReader,
                                                    ExxonMapper,
                                                    ExxonRecordParser
                                                    )

from oil_database.models.oil.values import UnittedValue


example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


def test_read_index():
    reader = ExxonDataReader(example_dir, example_index)

    assert reader.index is not None
    print(reader.index)
    assert reader.index == [('HOOPS Blend',
                             example_dir / 'Crude_Oil_HOOPS_Blend_assay_xls.xlsx'),
                            ]


def test_get_records():
    reader = ExxonDataReader(example_dir, example_index)

    records = reader.get_records()

    name, data = next(records)

    assert name == "HOOPS Blend"
    # some checking of the record
    assert data[5][0] == "HOOPS16F"
    # if more checks are needed: see next test

    # there should be only one
    with pytest.raises(StopIteration):
        next(records)


def test_read_excel_file():
    record = ExxonDataReader.read_excel_file(example_dir /
                                             "Crude_Oil_HOOPS_Blend_assay_xls.xlsx")

    pprint(record[:7])

    # there could be a LOT here, but just to make sure it isn't completely bonkers
    assert record[0][0] == "ExxonMobil"
    assert record


def test_ExxonRecordParser():
    """
    This is really a do-nothing function

    It's just a pass through
    """
    assert ExxonRecordParser("something random") == "something random"


class TestExxonMapper():
    """
    This is where the real work happens!
    """

    # fixme -- there should probably be a fixture to get a record
    record = next(ExxonDataReader(example_dir, example_index).get_records())
    oil = ExxonMapper(record)

    def test_header(self):
        oil = self.oil
        assert oil.name == 'HOOPS Blend'
        assert oil.reference.startswith("ExxonMobil")
        assert oil.api == 35.2

    def test_samples(self):
        samples = self.oil.samples

        assert len(samples) == 8
        assert samples[0].name == "Whole crude"

    def test_density(self):
        samples = self.oil.samples

        assert samples[0].densities[0].density.value == 0.84805316
        assert samples[7].densities[0].density.value == 0.99124762

    def test_cut_volume(self):
        samples = self.oil.samples

        assert samples[0].cut_volume == UnittedValue(100.0, unit="%")
        assert samples[3].cut_volume == UnittedValue(17.6059, unit="%")

    def test_compostion(self):
        samples = self.oil.samples
        # print(samples[0].carbon_mass_fraction)                 85.57594139885833
        assert samples[0].carbon_mass_fraction == UnittedValue(85.58, unit="%")
        assert samples[0].hydrogen_mass_fraction == UnittedValue(13.26, unit="%")
        assert samples[4].total_acid_number == UnittedValue(0.2069, unit="mg/kg")

    def test_viscosity(self):
        samples = self.oil.samples
        # viscosity tests
        # whole oil
        kvis = samples[0].kvis
        assert len(kvis) == 3
        assert kvis[0].viscosity.value == 6.73896867
        assert kvis[0].viscosity.unit == "cSt"
        assert kvis[2].viscosity.value == 3.88298696
        assert kvis[2].viscosity.unit == "cSt"

        # One sample
        kvis = samples[3].kvis
        assert len(kvis) == 3
        assert kvis[0].viscosity.value == 0.89317828
        assert kvis[0].viscosity.unit == "cSt"
        assert kvis[2].viscosity.value == 0.64536193
        assert kvis[2].viscosity.unit == "cSt"

        for sample in samples:
            assert len(sample.dvis) == 0

    def test_composition_mercaptan(self):
        samples = self.oil.samples
        assert samples[0].mercaptan_sulfur_mass_fraction.value == 0.5962

    def test_composition_nitrogen(self):
        samples = self.oil.samples
        assert samples[0].mercaptan_sulfur_mass_fraction.value == 0.5962

        assert samples[1].nitrogen_mass_fraction.value == 0.0
        assert samples[5].nitrogen_mass_fraction.value == 47.62

    def test_reid_vp(self):
        samples = self.oil.samples

        ## fixme -- is Pa the right unit?
        assert samples[0].reid_vapor_pressure.value == 60430.0

        for sample in samples[1:]:
            assert sample.reid_vapor_pressure is None


    def test_composition_ccr(self):
        samples = self.oil.samples
        assert samples[0].ccr_percent.value == 3.19

        assert samples[1].ccr_percent is None
        assert samples[6].ccr_percent.value == 0.3624


    composition_values = [("calcium_mass_fraction", (0,), (5.9,)),
                          ("hydrogen_sulfide_concentration", (), ()),
                          ("salt_content", (0,), (0.0026,)),
                          ("paraffin_volume_fraction", range(8), (35.54, 100.0, 91.91, 56.62, 42.77, 26.58, 18.99, 2.291 )),
                          ("naphthene_volume_fraction", range(8), (31.4, 0.0, 8.1, 33.2, 40.8, 47.5, 35.4, 13.4)),
                          ("aromatic_volume_fraction", range(8), (33.1, 0.0, 0.0, 10.2, 16.4, 26.0, 45.6, 84.3)),
                          ]
    @pytest.mark.parametrize("attr, indexes, values", composition_values)
    def test_comp(self, attr, indexes, values):
        samples = self.oil.samples

        print(attr)
        print(indexes)
        print(values)
        for i, val in zip(indexes, values):
            print(i, val)
            sample = samples[i]
            print(sample.calcium_mass_fraction)
            if val is None:
                assert getattr(sample, attr) is None
            else:
                assert isclose(getattr(sample, attr).value,
                               values[i], rel_tol=1e-2, abs_tol=1e-10)

    def test_dist_cuts_units(self):
        for sample in self.oil.samples:
            for cut in sample.distillation_cuts:
                assert cut.vapor_temp.unit == "C"
                assert cut.fraction.unit == "%"

    @pytest.mark.parametrize("samp_ind, cut_index, fraction, temp_f",
                             [(0, 0, 0.0, -57.64),
                              (0, 4, 30.0, 364.3),
                              (5, 9, 80.0, 615.3),
                              (7, 11, 95.0, 1436.0),
                              ])
    def test_dist_cuts(self, samp_ind, cut_index, fraction, temp_f):
        samples = self.oil.samples

        for cut in samples[samp_ind].distillation_cuts:
            print(cut)
        cut = samples[samp_ind].distillation_cuts[cut_index]
        assert cut.fraction.value == fraction
        assert isclose(cut.vapor_temp.value, uc.convert("F", "C", temp_f), rel_tol=1e-4)

    def test_no_cuts_in_butane(self):
        assert self.oil.samples[1].distillation_cuts == []





# def test_check():
#     record = next(ExxonDataReader(example_dir, example_index).get_records())
#     oil = ExxonMapper(record)

#     assert False
