"""
tests of the Exxon data importer

no very complete, because then I'd be pretty much re-writing a
lot of it (Or writing it all by hand)

but still handy to have some tests to run the code while under development
"""
import os
from pathlib import Path
from math import isclose
import json

import pytest

# skip these if openpyxl isn't there.
openpyxl = pytest.importorskip("openpyxl")


import nucos as uc

import adios_db
from adios_db.util import sigfigs
from adios_db.models.oil.oil import Oil
from adios_db.models.common.measurement import Temperature, VolumeFraction
try:
    # the tests should be skipped without openpyxl
    from adios_db.data_sources.exxon_assays import (ExxonDataReader,
                                                    ExxonMapper,
                                                    ExxonRecordParser)
except:
    pass

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing

output_dir = Path(__file__).resolve().parent / "output_dir"
example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


def test_read_index():
    reader = ExxonDataReader(example_index, example_dir)

    assert reader.index is not None
    assert reader.index == [
        {
            'name': 'HOOPS Blend',
            'path': example_dir / 'Crude_Oil_HOOPS_Blend_assay_xls.xlsx',
        },
        {
            'name': 'Liza',
            'path': example_dir / 'crude-oil_Liza_assay_jun2020_xls.xlsx',
        },
    ]


def test_get_records():
    reader = ExxonDataReader(example_index, example_dir)
    records = reader.get_records()
    name, [data, *_] = next(records)

    assert name == "HOOPS Blend"

    # some checking of the record
    assert data[5][0] == "HOOPS16F"

    # if more checks are needed: see next test

    # there should be only two
    with pytest.raises(StopIteration):
        next(records)
        next(records)


def test_read_excel_file():
    record = ExxonDataReader.read_excel_file(
        example_dir / "Crude_Oil_HOOPS_Blend_assay_xls.xlsx"
    )

    # there could be a LOT here, but just to make sure it isn't completely
    # bonkers
    assert record

    # [sheet][row][col]
    assert record[0][0][0] == "ExxonMobil"


def test_ExxonRecordParser():
    """
    This is really a do-nothing function

    It's just a pass through
    """
    assert ExxonRecordParser("something random", None) == ("something random",
                                                           None)


def test_full_round_trip():
    """
    This test makes sure that it can read a full record,
    save it as JSON, and then read it back again
    """
    record = ExxonDataReader.read_excel_file(
        example_dir / "Crude_Oil_HOOPS_Blend_assay_xls.xlsx"
    )

    assert record[0][0][0] == "ExxonMobil"

    oil = ExxonMapper(('HOOPS Blend Example', record))

    assert oil.metadata.name == 'HOOPS Blend Example'

    print(oil.oil_id)

    filename = output_dir / "ExampleOutput.json"
    oil.to_file(filename)

    oil2 = Oil.from_file(filename)

    for bc2, bc in zip(oil2.sub_samples[0].bulk_composition,
                       oil.sub_samples[0].bulk_composition):
        assert bc2 == bc

    assert oil2.sub_samples[0].bulk_composition == oil.sub_samples[0].bulk_composition
    assert oil2.sub_samples[0].industry_properties == oil.sub_samples[0].industry_properties
    assert oil2 == oil


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

        assert oil.metadata.name == 'HOOPS Blend'
        assert oil.metadata.reference.reference.startswith("ExxonMobil")
        assert oil.metadata.API == 35.2

    @pytest.mark.parametrize("index, expected", [
        (0, {
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
        assert samples[index].metadata.name == expected['name']
        assert samples[index].metadata.short_name == expected['short_name']

    @pytest.mark.parametrize("index, expected", [
        (0, None),
        (1, Temperature(min_value=-57.641, max_value=60.0, unit='F')),
        (2, Temperature(min_value=60.0, max_value=165.0, unit='F')),
        (3, Temperature(min_value=165.0, max_value=330.0, unit='F')),
        (4, Temperature(min_value=330.0, max_value=480.0, unit='F')),
        (5, Temperature(min_value=480.0, max_value=650.0, unit='F')),
        (6, Temperature(min_value=650.0, max_value=1000.0, unit='F')),
        (7, Temperature(min_value=1000.0, max_value=1504.6, unit='F')),
    ])
    def test_boiling_point_range(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert len(samples) == 8
        assert samples[index].metadata.boiling_point_range == expected

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

    @pytest.mark.parametrize("sample_idx, density_idx, expected", [
        (0, 0, 0.84805),
        (7, 0, 0.99125),
    ])
    def test_densities(self, sample_idx, density_idx, expected):
        samples = ExxonMapper(self.record).sub_samples
        sample = samples[sample_idx]
        density = sample.physical_properties.densities[density_idx]

        assert isclose(density.density.value, expected, rel_tol=1e-3)

    @pytest.mark.parametrize("sample_idx, viscosity_idx, expected", [
        (0, 0, 6.739),
        (0, 2, 3.883),
        (3, 0, 0.89318),
        (3, 2, 0.64536),
    ])
    def test_kinematic_viscosities(self, sample_idx, viscosity_idx, expected):
        samples = ExxonMapper(self.record).sub_samples
        sample = samples[sample_idx]
        phys = sample.physical_properties
        viscosity = phys.kinematic_viscosities[viscosity_idx]

        # viscosity tests
        # whole oil
        assert viscosity.viscosity.value == expected
        assert viscosity.viscosity.unit == "cSt"

        for sample in samples:
            assert len(sample.physical_properties.dynamic_viscosities) == 0

    def test_dynamic_viscosities(self):
        samples = ExxonMapper(self.record).sub_samples

        for sample in samples:
            # no dynamic viscosities in the Exxon Assays
            assert len(sample.physical_properties.dynamic_viscosities) == 0

    @pytest.mark.parametrize("attr, indexes, values", [
        ('Sulfur Mass Fraction', range(8),
         (1.1494, 0.00019105, 0.0024387, 0.019791,
          0.11793, 0.76024, 1.5844, 3.047)),
        ('Naphthene Volume Fraction', range(8),
         (31.362, 0.0, 8.0856, 33.16, 40.822, 47.458, 35.381, 13.435)),
        ('Paraffin Volume Fraction', range(8),
         (35.538, 100.0, 91.914, 56.621, 42.772, 26.58, 18.992, 2.2913)),
        ('Nickel Mass Fraction', range(8),
         (8.183, None, None, None, None, None, None, 46.969)),
        ('Vanadium Mass Fraction', range(8),
         (17.215, None, None, None, None, None, None, 98.808)),
        ('Carbon Mass Fraction', range(8),
         (85.58, 82.43, 83.64, 85.43, 85.86, 86.06, 85.87, 85.43)),
        ('Hydrogen Mass Fraction', range(8),
         (13.26, 17.57, 16.36, 14.57, 14.04, 13.09, 12.36, 11.8)),
        ('Mercaptan Sulfur Mass Fraction', range(8),
         (0.5962, 0.7594, 8.106, 45.26, 32.83, 20.2, 3.227, 0.07651)),
        ('Nitrogen Mass Fraction', range(8),
         (968.12, 0.0, 0.0, 0.061811, 1.7976, 47.62, 782.36, 4176.0)),
        ('Calcium Mass Fraction', range(8), (5.9, None, None, None,
                                             None, None, None, None)),
        ('Hydrogen Sulfide Concentration', range(8),
         (0.0, None, None, None, None, None, None, None)),
        ('Salt Content', range(8), (0.0026, None, None, None,
                                    None, None, None, None)),
    ])
    def test_bulk_composition(self, attr, indexes, values):
        """
        Data points that are classified in bulk composition:
        - Sulphur
        - Naphthenes
        - Paraffins
        - Nickel
        - Vanadium
        - Carbon
        - Hydrogen
        - Mercaptan Sulfur
        - Nitrogen
        - Calcium
        - Hydrogen Sulfide
        - Salt content

        Notes:
        - These values are now kept in a list of compounds held by the
          bulk_composition attribute
        - Ideally, the name & groups of each compound would have the
          original field text from the datasheet.  This is not the case
          at present.
        """
        samples = ExxonMapper(self.record).sub_samples

        for i, val in zip(indexes, values):
            filter_list = [c for c in samples[i].bulk_composition
                           if c.name == attr]

            if val is None:
                assert len(filter_list) == 0
            else:
                assert len(filter_list) == 1

                compound = filter_list[0]

                assert isclose(compound.measurement.value, values[i],
                               rel_tol=1e-4)

    @pytest.mark.parametrize("attr, indexes, values", [
        ('Total Acid Number', range(8),
         (0.90915, 8.294e-08, 4.8689e-05, 0.004045,
          0.20694, 1.3179, 1.8496, 0.6179)),
        ('Reid Vapor Pressure', range(8), (8.7651, None, None, None,
                                           None, None, None, None)),
        ('Aniline Point', range(8),
         (None, None, None, None, 140.679, 155.3736, 177.6938, None)),
        ('Cetane Index 1990 (D4737)', range(8),
         (None, None, None, 36.2293, 45.0055, 49.9756, None, None)),
        ('Cloud Point', range(8),
         (None, None, None, -106.574729, -62.385169, 4.0361, None, None)),
        ('Smoke Point', range(8), (None, None, None, 29.8541,
                                   22.4655, 13.7602, None, None)),
        ('Conradson Carbon Residue', range(8),
         (3.1904, None, None, None, None, None, 0.36241, 17.695)),
        ('Freeze Point', range(8),
         (None, None, None, -99.2151, -54.7016, 14.6042, None, None)),
    ])
    def test_industry_properties(self, attr, indexes, values):
        """
        Data points that are classified in industry properties:
        - Total Acid Number (Neutralization Number)
        - Reid Vapor Pressure

        - Aniline Point
        - Cetane Index
        - Vanadium
        - Cloud Point
        - Smoke Point
        - Conradson Carbon Residue
        - Conradson Residuum (Vacuum Residue)
        - Gel Point (Freeze Point)

        Notes:
        - These values are kept in a list of attributes held by the
          industry_properties attribute
        - Ideally, the name & groups of each compound would have the
          original field text from the datasheet.  This is not the case
          at present.
        """
        samples = ExxonMapper(self.record).sub_samples

        for i, val in zip(indexes, values):
            filter_list = [c for c in samples[i].industry_properties
                           if c.name == attr]
            if val is None:
                assert len(filter_list) == 0
            else:
                assert len(filter_list) == 1

                compound = filter_list[0]

                assert isclose(compound.measurement.value, values[i],
                               rel_tol=1e-4)

    @pytest.mark.parametrize("prop, unit, unit_type", [
        ('Total Acid Number', 'mg/g', 'massfraction'),
        ('Reid Vapor Pressure', 'psi', 'pressure'),
        ('Aniline Point', 'F', 'temperature'),
        ('Cetane Index 1990 (D4737)', None, 'unitless'),
        ('Cloud Point', 'F', 'temperature'),
        ('Smoke Point', 'mm', 'length'),
        ('Freeze Point', 'F', 'temperature'),
    ])
    def test_industry_properties_units(self, prop, unit, unit_type):
        """
        Data points that are classified in industry properties:
        - Total Acid Number (Neutralization Number)
        - Reid Vapor Pressure

        - Aniline Point
        - Cetane Index
        - Vanadium
        - Cloud Point
        - Smoke Point
        - Conradson Carbon Residue
        - Conradson Residuum (Vacuum Residue)
        - Gel Point (Freeze Point)
        """
        # just check the zeroth one:

        print("testing:", prop)

        for sample in ExxonMapper(self.record).sub_samples:
            for p in sample.industry_properties:
                if p.name == prop:
                    assert p.measurement.unit == unit
                    assert p.measurement.unit_type == unit_type

                    return

                continue

        assert False
        # assert False, f"property: {p.name} is missing"

    @pytest.mark.parametrize("attr, indexes, values", [
        ('saturates', range(8), [None, None, None, None,
                                 None, None, None, None]),
        ('aromatics', range(8), [None, None, None, None,
                                 None, None, None, None]),
        ('resins', range(8), [None, None, None, None,
                              None, None, None, None]),
        ('asphaltenes', range(8), [None, None, None, None,
                                   None, None, None, None]),
    ])
    def test_sara(self, attr, indexes, values):
        """
        Test the sara attributes:
        - Aromatics
        - Asphaltenes

        Note: saturates and resins are not found in the Exxon Assays
        Note: We have decided that instead of C7 asphaltenes & aromatics
              going into SARA, we will put them into the bulk_composition
              list.
        """
        samples = ExxonMapper(self.record).sub_samples

        for i, val in zip(indexes, values):
            sara = samples[i].SARA

            if val is None:
                assert getattr(sara, attr) is None
            else:
                sara_attr = getattr(sara, attr)

                assert isclose(sara_attr.value, values[i], rel_tol=1e-4)

    def test_dist_cuts_units(self):
        for sample in ExxonMapper(self.record).sub_samples:
            for cut in sample.distillation_data.cuts:
                assert cut.vapor_temp.unit == "C"
                assert cut.fraction.unit == "%"

    def test_dist_type(self):
        for sample in ExxonMapper(self.record).sub_samples:
            assert sample.distillation_data.type == 'volume fraction'

    @pytest.mark.parametrize("samp_ind, cut_index, fraction, temp_f", [
        (0, 0, 0.0, -57.641),
        (0, 4, 30.0, 364.28),
        (5, 9, 80.0, 615.34),
        (7, 11, 95.0, 1435.99),
    ])
    def test_dist_cuts(self, samp_ind, cut_index, fraction, temp_f):
        samples = ExxonMapper(self.record).sub_samples

        cut = samples[samp_ind].distillation_data.cuts[cut_index]

        assert cut.fraction.value == fraction
        assert isclose(cut.vapor_temp.value,
                       sigfigs(uc.convert("F", "C", temp_f), 5),
                       rel_tol=1e-4)

    @pytest.mark.parametrize("sample_idx, expected", [
        (0, 1453.75),
        (1, None),
        (5, 649.13),
        (7, 1504.63),
    ])
    def test_dist_end_point(self, sample_idx, expected):
        samples = ExxonMapper(self.record).sub_samples

        if expected is None:
            assert samples[sample_idx].distillation_data.end_point is None
        else:
            expected_c = sigfigs(uc.convert("F", "C", expected), 5)
            end_point = samples[sample_idx].distillation_data.end_point

            assert isclose(end_point.value, expected_c, rel_tol=1e-4)
            assert end_point.unit == 'C'

    def test_no_cuts_in_butane(self):
        assert (ExxonMapper(self.record)
                .sub_samples[1].distillation_data.cuts == [])

    def test_save_to_json(self):
        """
        Save an example .json file.  This is not so much a test, but a job
        to provide sample data that people can look at.
        """
        mapper = ExxonMapper(self.record)
        py_json = mapper.py_json()

        py_json['status'] = []

        filename = 'EX-Example-Record.json'
        file_path = os.path.sep.join(
            adios_db.__file__.split(os.path.sep)[:-3] + ['examples', filename]
        )

        print(f'saving to: {file_path}')
        with open(file_path, 'w', encoding="utf-8") as fd:
            json.dump(py_json, fd, indent=4, sort_keys=True)
