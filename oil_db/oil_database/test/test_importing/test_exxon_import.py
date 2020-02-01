"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""
from pathlib import Path
from pprint import pprint

import pytest

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

    def test_dist_cuts(self):
        samples = self.oil.samples

        assert samples[0].cut_volume == UnittedValue(100.0, unit="%")
        assert samples[3].cut_volume == UnittedValue(17.6059, unit="%")

    def test_density(self):
        samples = self.oil.samples

        assert samples[0].densities[0].density.value == 0.84805316
        assert samples[7].densities[0].density.value == 0.99124762

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

    def test_exxon_mapper(self):
        samples = self.oil.samples






