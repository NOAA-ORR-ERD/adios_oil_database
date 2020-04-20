"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""
from pathlib import Path
from math import isclose

import pytest

import unit_conversion as uc

from oil_database.data_sources.exxon_assays import (ExxonDataReader,
                                                    ExxonMapper,
                                                    ExxonRecordParser
                                                    )

from oil_database.models.common.measurement import (Temperature,
                                                    VolumeFraction)

example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


def test_read_index():
    reader = ExxonDataReader(example_index, example_dir)

    assert reader.index is not None
    assert reader.index == [(
        'HOOPS Blend',
        example_dir / 'Crude_Oil_HOOPS_Blend_assay_xls.xlsx'
    )]


def test_get_records():
    reader = ExxonDataReader(example_index, example_dir)

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
    record = ExxonDataReader.read_excel_file(
        example_dir / "Crude_Oil_HOOPS_Blend_assay_xls.xlsx"
    )

    # there could be a LOT here, but just to make sure it isn't completely
    # bonkers
    assert record[0][0] == "ExxonMobil"
    assert record


def test_ExxonRecordParser():
    """
    This is really a do-nothing function

    It's just a pass through
    """
    assert ExxonRecordParser("something random", None) == ("something random",
                                                           None)


class TestExxonMapper():
    """
    This is where the real work happens!
    """

    # fixme -- there should probably be a fixture to get a record
    record = next(ExxonDataReader(example_index, example_dir).get_records())

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = ExxonMapper()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _mapper = ExxonMapper(None)

    def test_header(self):
        oil = ExxonMapper(self.record)

        assert oil.name == 'HOOPS Blend'
        assert oil.reference.startswith("ExxonMobil")
        assert oil.API == 35.2

    @pytest.mark.parametrize("index, expected",
                             [(0, {
                                 'name': 'Fresh Oil Sample',
                                 'short_name': 'Fresh Oil',
                               }),
                              (1, {
                                 'name': 'Butane and Lighter IBP - 60F',
                                 'short_name': 'Butane and L...',
                               }),
                              (2, {
                                 'name': 'Lt. Naphtha C5 - 165F',
                                 'short_name': 'Lt. Naphtha ...',
                               }),
                              (3, {
                                 'name': 'Hvy Naphtha 165 - 330F',
                                 'short_name': 'Hvy Naphtha ...',
                               }),
                              (4, {
                                 'name': 'Kerosene 330 - 480F',
                                 'short_name': 'Kerosene 330...'
                               }),
                              (5, {
                                 'name': 'Diesel 480 - 650F',
                                 'short_name': 'Diesel 480 -...'
                               }),
                              (6, {
                                 'name': 'Vacuum Gas Oil 650 - 1000F',
                                 'short_name': 'Vacuum Gas O...'
                               }),
                              (7, {
                                 'name': 'Vacuum Residue 1000F+',
                                 'short_name': 'Vacuum Resid...'
                               }),
                              ])
    def test_sample_ids(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert len(samples) == 8
        assert samples[index].name == expected['name']
        assert samples[index].short_name == expected['short_name']

    @pytest.mark.parametrize("index, expected", [
        (0, None),
        (1, Temperature(min_value=-57.64149540757175, max_value=60.0,
                        unit='F')),
        (2, Temperature(min_value=60.0, max_value=165.0, unit='F')),
        (3, Temperature(min_value=165.0, max_value=330.0, unit='F')),
        (4, Temperature(min_value=330.0, max_value=480.0, unit='F')),
        (5, Temperature(min_value=480.0, max_value=650.0, unit='F')),
        (6, Temperature(min_value=650.0, max_value=1000.0, unit='F')),
        (7, Temperature(min_value=1000.0, max_value=1504.6348493781763,
                        unit='F')),
    ])
    def test_boiling_point_range(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert len(samples) == 8
        assert samples[index].boiling_point_range == expected

    @pytest.mark.parametrize("index, expected", [
        (0, VolumeFraction(100.0, unit="%")),
        (1, VolumeFraction(value=2.3128, unit='%')),
        (2, VolumeFraction(value=6.6891, unit='%')),
        (3, VolumeFraction(value=17.6059, unit='%')),
        (4, VolumeFraction(value=14.6657, unit='%')),
        (5, VolumeFraction(value=16.6362, unit='%')),
        (6, VolumeFraction(value=27.1985, unit='%')),
        (7, VolumeFraction(value=14.8918, unit='%')),
    ])
    def test_cut_volume(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert samples[index].cut_volume == expected

    def test_density(self):
        samples = ExxonMapper(self.record).sub_samples

        assert samples[0].physical_properties.densities[0].density.value == 0.84805316
        assert samples[7].physical_properties.densities[0].density.value == 0.99124762

    def test_viscosity(self):
        samples = ExxonMapper(self.record).sub_samples

        # viscosity tests
        # whole oil
        kvis = samples[0].physical_properties.kinematic_viscosities
        assert len(kvis) == 3
        assert kvis[0].viscosity.value == 6.73896867
        assert kvis[0].viscosity.unit == "cSt"
        assert kvis[2].viscosity.value == 3.88298696
        assert kvis[2].viscosity.unit == "cSt"

        # One sample
        kvis = samples[3].physical_properties.kinematic_viscosities
        assert len(kvis) == 3
        assert kvis[0].viscosity.value == 0.89317828
        assert kvis[0].viscosity.unit == "cSt"
        assert kvis[2].viscosity.value == 0.64536193
        assert kvis[2].viscosity.unit == "cSt"

        for sample in samples:
            assert len(sample.physical_properties.dynamic_viscosities) == 0

    @pytest.mark.parametrize("attr, indexes, values", [
        ('Carbon Mass Fraction', range(8), (85.58, 82.43, 83.64, 85.43,
                                            85.86, 86.06, 85.87, 85.43)),
        ('Hydrogen Mass Fraction', range(8), (13.26, 17.57, 16.36, 14.57,
                                              14.04, 13.09, 12.36, 11.8)),
        ('Total Acid Number', range(8), (0.9092, 8.294e-08, 4.869e-05,
                                         0.004045, 0.2069, 1.318, 1.85,
                                         0.6179)),
        ('Sulfur Mass Fraction', range(8), (1.149, 0.000191, 0.002439, 0.01979,
                                            0.1179, 0.7602, 1.584, 3.047)),
        ('Mercaptan Sulfur Mass Fraction',
         range(8), (0.5962, 0.7594, 8.106, 45.26,
                    32.83, 20.2, 3.227, 0.07651)
         ),
        ('Nitrogen Mass Fraction', range(8), (968.1, 0.0, 0.0, 0.06181,
                                              1.798, 47.62, 782.4, 4176.0)),
        ('Conradson Carbon Residue', range(8), (3.19, None, None, None,
                                                None, None, 0.3624, 17.69)),
        ('N-Heptane Insolubles (C7 Asphaltenes)',
         range(8), (0.3427, None, None, None,
                    None, None, 0.0, 1.967)
         ),
        ('Nickel Mass Fraction', range(8), (8.2, None, None, None,
                                            None, None, None, 47.0)),
        ('Vanadium Mass Fraction', range(8), (17.21, None, None, None,
                                              None, None, None, 98.81)),
        ('Calcium Mass Fraction', range(8), (5.9, None, None, None,
                                             None, None, None, None)),
        ('Reid Vapor Pressure', range(8), (60430.0, None, None, None,
                                           None, None, None, None)),
        ('Hydrogen Sulfide Concentration', range(8), (0.0, None, None, None,
                                                      None, None, None, None)),
        ('Salt Content', range(8), (0.0026, None, None, None,
                                    None, None, None, None)),
        ('Paraffin Volume Fraction', range(8), (35.54, 100.0, 91.91, 56.62,
                                                42.77, 26.58, 18.99, 2.291)),
        ('Naphthene Volume Fraction', range(8), (31.4, 0.0, 8.1, 33.2,
                                                 40.8, 47.5, 35.4, 13.4)),
        ('Aromatic Volume Fraction', range(8), (33.1, 0.0, 0.0, 10.2,
                                                16.4, 26.0, 45.6, 84.3)),
        ('Naphthalene Volume Fraction', range(8), (None, None, None, None,
                                                   1.044, 8.591, None, None)),
        # ('Freeze Point', (), ()),
        # ('Smoke Point', (), ()),
        # ('Cetane Index 1990 (D4737)', (), ()),
        # ('Cloud Point', (), ()),
        # ('Aniline Point', (), ()),
    ])
    def test_bulk_composition(self, attr, indexes, values):
        '''
            Notes:
            - These values are now kept in a list of compounds held by the
              bulk_composition attribute
            - Ideally, the name & groups of each compound would have the
              original field text from the datasheet.  This is not the case
              at present.
        '''
        samples = ExxonMapper(self.record).sub_samples

        for i, val in zip(indexes, values):
            filter_list = [c for c in samples[i].bulk_composition
                           if c.name == attr]
            if val is None:
                assert len(filter_list) == 0
            else:
                assert len(filter_list) == 1

                compound = filter_list[0]

                assert isclose(compound.measurement.value,
                               values[i], rel_tol=1e-2, abs_tol=1e-10)

    def test_dist_cuts_units(self):
        for sample in ExxonMapper(self.record).sub_samples:
            for cut in sample.distillation_data:
                assert cut.vapor_temp.unit == "C"
                assert cut.fraction.unit == "%"

    @pytest.mark.parametrize("samp_ind, cut_index, fraction, temp_f",
                             [(0, 0, 0.0, -57.64),
                              (0, 4, 30.0, 364.3),
                              (5, 9, 80.0, 615.3),
                              (7, 11, 95.0, 1436.0),
                              ])
    def test_dist_cuts(self, samp_ind, cut_index, fraction, temp_f):
        samples = ExxonMapper(self.record).sub_samples

        cut = samples[samp_ind].distillation_data[cut_index]

        assert cut.fraction.value == fraction
        assert isclose(cut.vapor_temp.value, uc.convert("F", "C", temp_f),
                       rel_tol=1e-4)

    def test_no_cuts_in_butane(self):
        assert ExxonMapper(self.record).sub_samples[1].distillation_data == []
