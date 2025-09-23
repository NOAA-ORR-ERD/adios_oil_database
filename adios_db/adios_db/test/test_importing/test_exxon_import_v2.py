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

import adios_db
try:
    # the tests should be skipped without openpyxl
    from adios_db.data_sources.exxon_assays import ExxonDataReader, ExxonMapper
except:
    pass

from adios_db.models.common.measurement import (Temperature, VolumeFraction)

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing


example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"


# Note: No need to test the reader or the parser. They have not changed from V1
#       We will only need to test the mapper.


class TestExxonMapper():
    @classmethod
    def setup_class(cls):
        it = ExxonDataReader(example_index, example_dir).get_records()
        next(it)
        cls.record = next(it)  # 2nd record

    def test_init_empty(self):
        with pytest.raises(TypeError):
            _mapper = ExxonMapper()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _mapper = ExxonMapper(None)

    def test_oil_metadata(self):
        oil = ExxonMapper(self.record)

        assert oil.metadata.name == 'Liza'
        assert oil.metadata.source_id == 'LIZA20X'
        assert oil.metadata.location == 'Guyana'
        assert oil.metadata.reference.reference.startswith("ExxonMobil")
        assert oil.metadata.product_type == 'Crude Oil NOS'
        assert oil.metadata.sample_date == '2020-05-04T00:00:00'
        assert oil.metadata.API == 32.0
        assert oil.metadata.comments is None

    @pytest.mark.parametrize("index, expected", [
        (0, {
            'name': 'Fresh Oil Sample',
            'short_name': 'Fresh Oil',
        }),
        (1, {
            'name': 'C5 - 149 (Atmospheric Cut)',
            'short_name': 'C5 - 149 (At...',
        }),
        (2, {
            'name': '149 - 212 (Atmospheric Cut)',
            'short_name': '149 - 212 (A...',
        }),
        (3, {
            'name': '212 - 302 (Atmospheric Cut)',
            'short_name': '212 - 302 (A...',
        }),
        (4, {
            'name': '302 - 392 (Atmospheric Cut)',
            'short_name': '302 - 392 (A...'
        }),
        (5, {
            'name': '392 - 482 (Atmospheric Cut)',
            'short_name': '392 - 482 (A...'
        }),
        (6, {
            'name': '482 - 572 (Atmospheric Cut)',
            'short_name': '482 - 572 (A...'
        }),
        (7, {
            'name': '572 - 662 (Atmospheric Cut)',
            'short_name': '572 - 662 (A...'
        }),
        (8, {
            'name': '662 - 698 (Atmospheric Cut)',
            'short_name': '662 - 698 (A...'
        }),
        (9, {
            'name': '698 - FBP (Atmospheric Cut)',
            'short_name': '698 - FBP (A...'
        }),
        (10, {
            'name': '698 - 842 (Vacuum Cut)',
            'short_name': '698 - 842 (V...'
        }),
        (11, {
            'name': '842 - 932 (Vacuum Cut)',
            'short_name': '842 - 932 (V...'
        }),
        (12, {
            'name': '932 - 1022 (Vacuum Cut)',
            'short_name': '932 - 1022 (...'
        }),
        (13, {
            'name': '1022 - FBP (Vacuum Cut)',
            'short_name': '1022 - FBP (...'
        }),
    ])
    def test_sample_ids(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert len(samples) == 14
        assert samples[index].metadata.name == expected['name']
        assert samples[index].metadata.short_name == expected['short_name']

    @pytest.mark.parametrize("index, expected", [
        (0, None),
        (1, Temperature(min_value=49.0, max_value=149.0, unit='F')),
        (2, Temperature(min_value=149.0, max_value=212.0, unit='F')),
        (3, Temperature(min_value=212.0, max_value=302.0, unit='F')),
        (4, Temperature(min_value=302.0, max_value=392.0, unit='F')),
        (5, Temperature(min_value=392.0, max_value=482.0, unit='F')),
        (6, Temperature(min_value=482.0, max_value=572.0, unit='F')),
        (7, Temperature(min_value=572.0, max_value=662.0, unit='F')),
        (8, Temperature(min_value=662.0, max_value=698.0, unit='F')),
        (9, Temperature(min_value=698.0, max_value=1228.0, unit='F')),
        (10, Temperature(min_value=698.0, max_value=842.0, unit='F')),
        (11, Temperature(min_value=842.0, max_value=932.0, unit='F')),
        (12, Temperature(min_value=932.0, max_value=1022.0, unit='F')),
        (13, Temperature(min_value=1022.0, max_value=1228.0, unit='F')),
    ])
    def test_boiling_point_range(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert len(samples) == 14
        assert samples[index].metadata.boiling_point_range == expected

    @pytest.mark.parametrize("index, expected", [
        (0, VolumeFraction(100.0, unit="%")),
        (1, VolumeFraction(value=3.76912, unit='%')),
        (2, VolumeFraction(value=5.14542, unit='%')),
        (3, VolumeFraction(value=8.15915, unit='%')),
        (4, VolumeFraction(value=7.93166, unit='%')),
        (5, VolumeFraction(value=8.27995, unit='%')),
        (6, VolumeFraction(value=9.05842, unit='%')),
        (7, VolumeFraction(value=9.20427, unit='%')),
        (8, VolumeFraction(value=3.56733, unit='%')),
        (9, VolumeFraction(value=43.3804, unit='%')),
        (10, VolumeFraction(value=13.712, unit='%')),
        (11, VolumeFraction(value=7.55082, unit='%')),
        (12, VolumeFraction(value=6.23317, unit='%')),
        (13, VolumeFraction(value=15.8843, unit='%')),
    ])
    def test_cut_volume(self, index, expected):
        samples = ExxonMapper(self.record).sub_samples

        assert samples[index].cut_volume == expected

    @pytest.mark.parametrize("sample_idx, density_idx, expected", [
        (0, 0, 0.86505),
        (1, 0, 0.64246),
        (2, 0, 0.72601),
        (3, 0, 0.7598),
        (4, 0, 0.79557),
        (5, 0, 0.82449),
        (6, 0, 0.84972),
        (7, 0, 0.86496),
        (8, 0, 0.88531),
        (9, 0, 0.94837),
        (10, 0, 0.90317),
        (11, 0, 0.9249),
        (12, 0, 0.93608),
        (13, 0, 1.0034),
    ])
    def test_densities(self, sample_idx, density_idx, expected):
        samples = ExxonMapper(self.record).sub_samples
        sample = samples[sample_idx]
        density = sample.physical_properties.densities[density_idx]

        assert isclose(density.density.value, expected, rel_tol=1e-3)

    @pytest.mark.parametrize("sample_idx, viscosity_idx, expected", [
        (0, 0, 15.331),
        (0, 2, 5.9194),
        (9, 0, 691.09),
        (9, -1, 44.706),
        (13, 0, 3254.9),
        (13, -1, 471.04),
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
        ('Sulfur Mass Fraction', range(14),
         (0.5839, 0.000017074, 0.00029992, 0.0046359, 0.035549, 0.10686,
          0.26023, 0.4343, 0.5292, 1.0274, 0.6252, 0.7878, 0.9629, 1.4684)),
        ('Mercaptan Sulfur Mass Fraction', range(14),
         (5.0, 0.00001487, 0.001954, 0.1061, 1.294, 2.362, 1.416,
          None, None, None, None, None, None, None)),
        ('Nitrogen Mass Fraction', range(14),
         (1740.7, None, None, None, None, 10.083, 58.58,
          248.0, 525.99, 3549.4, 1165.0, 2128.74, 2993.38, 6228.27)),
        ('Paraffin Mass Fraction', range(14),
         (27.2, 94.03, 51.32, 32.934, 39.82, None, None,
          None, None, None, None, None, None, None)),
        ('Naphthene Mass Fraction', range(14),
         (37.674, 5.962, 47.27, 57.14, 47.71, None, None,
          None, None, None, None, None, None, None)),
        ('Aromatics', range(14),
         (35.127, 0.0, 1.4162, 9.9257, 12.469, None, None,
          None, None, None, None, None, None, None)),
        ('Naphthalene Volume Fraction', range(14),
         (None, None, None, None, 0.13034, 2.8632, 6.7458,
          8.3017, None, None, None, None, None, None)),
        ('Hydrogen Mass Fraction', range(14),
         (None, 16.49, 15.21, 14.34, 14.16, 13.61, 13.45,
          13.25, 12.84, None, 12.68, 12.57, 12.68, None)),
        ('Wax Mass Fraction', range(14),
         (None, None, None, None, None, None, None,
          None, None, None, None, None, None, None)),
        ('C7 Asphaltene Mass Fraction', range(14),
         (0.3473, None, None, None, None, None, None,
          None, None, 0.72836, None, 0.0, 0.0, 1.88)),
        ('Vanadium Mass Fraction', range(14),
         (23.474, None, None, None, None, None, None,
          None, None, 49.23, None, 0.0, 0.0, 127.08)),
        ('Nickel Mass Fraction', range(14),
         (15.96, None, None, None, None, None, None,
          None, None, 33.47, None, 0.0, 0.0, 86.4)),
        ('Iron Mass Fraction', range(14),
         (0.545, None, None, None, None, None, None,
          None, None, 5.0754, None, 0.0, 0.0, 13.101)),
        ('Salt Content', range(14),
         (0.02, None, None, None, None, None, None,
          None, None, None, None, None, None, None)),
        ('Hydrogen Sulfide Concentration', range(14),
         (None, None, None, None, None, None, None,
          None, None, None, None, None, None, None)),
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
        ('Total Acid Number', range(14),
         (0.23668, 0.0062798, 0.024283, 0.06108, 0.10284, 0.14545, 0.19295,
          0.24499, 0.29098, 0.33883, 0.34904, 0.38876, 0.38964, 0.2904)),
        ('Cloud Point', range(14),
         (None, None, None, None, None, -53.113, -9.0168,
          33.6, None, None, None, None, None, None)),
        ('Freeze Point', range(14),
         (None, None, None, None, -79.346, -44.66, -4.9233,
          None, None, None, None, None, None, None)),
        ('Smoke Point', range(14),
         (None, None, None, None, 25.267, 21.07, 17.491,
          None, None, None, None, None, None, None)),
        ('Cetane Index', range(14),
         (None, None, None, None, 35.729, 43.084, 49.404,
          58.064, 59.42, None, None, None, None, None)),
        ('Aniline Point', range(14),
         (None, None, None, 126.67, 131.76, 141.27, 156.87,
          171.39, 176.25, None, 190.16, 206.74, 208.71, None)),
        ('Micro Carbon Residue', range(14),
         (3.3672, None, None, None, None, None, None,
          None, None, 7.0616, None, 0.060065, 1.1285, 17.789)),
        ('Reid Vapor Pressure', range(14),
         (5.7187, None, None, None, None, None, None,
          None, None, None, None, None, None, None)),
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
        ('Cloud Point', 'F', 'temperature'),
        ('Freeze Point', 'F', 'temperature'),
        ('Smoke Point', 'mm', 'length'),
        ('Cetane Index 1990 (D4737)', None, 'unitless'),
        ('Aniline Point', 'F', 'temperature'),
        ('Conradson Carbon Residue', '%', 'massfraction'),
        ('Reid Vapor Pressure', 'psi', 'pressure'),
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

        for sample in ExxonMapper(self.record).sub_samples:
            for p in sample.industry_properties:
                if p.name == prop:
                    measurement = p.measurement
                    assert measurement.unit == unit
                    assert measurement.unit_type == unit_type
                    return
                continue

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

    @pytest.mark.parametrize("attr, value", [
        ('Methane + Ethane', 0.084485),
        ('Propane', 0.25222),
        ('Isobutane', 0.16142),
        ('N-Butane', 0.69613),
        ('Isopentane', 0.6078),
        ('N-Pentane', 0.79702),
        ('Cyclopentane', 0.14124),
        ('C6 Paraffins', 1.5586),
        ('C6 Naphthenes', None),
        ('Benzene', 0.06012),
        ('C7 Paraffins', 1.4452),
        ('C7 Naphthenes', None),
        ('Toluene', 0.2786),
    ])
    def test_molecules(self, attr, value):
        # Only the first sample will have molecule attributes
        # They will be located in the sample compounds list
        sample = ExxonMapper(self.record).sub_samples[0]

        filter_list = [c for c in sample.compounds
                       if c.name == attr]
        if value is None:
            assert len(filter_list) == 0
        else:
            assert len(filter_list) == 1

            compound = filter_list[0]

            assert isclose(compound.measurement.value, value, rel_tol=1e-4)

    def test_dist_cuts_units(self):
        for sample in ExxonMapper(self.record).sub_samples:
            for cut in sample.distillation_data.cuts:
                assert cut.vapor_temp.unit == "F"
                assert cut.fraction.unit == "%"

    def test_dist_type(self):
        # only the first sample will have distillation
        sample = ExxonMapper(self.record).sub_samples[0]

        assert sample.distillation_data.type == 'mass fraction'

    @pytest.mark.parametrize("samp_ind, cut_index, fraction, temp_f", [
        (0, 0, 0.071146, -122.0),
        (0, 46, 18.819, 346.0),  # midpoint
        (0, -1, 92.395, 1228.0),  # last cut
        (0, 95, 92.395, 1228.0),  # to test the length is correct
    ])
    def test_dist_cuts(self, samp_ind, cut_index, fraction, temp_f):
        # only the first sample will have distillation
        samples = ExxonMapper(self.record).sub_samples

        cut = samples[samp_ind].distillation_data.cuts[cut_index]

        assert isclose(cut.fraction.value, fraction, rel_tol=1e-4)
        assert isclose(cut.vapor_temp.value, temp_f, rel_tol=1e-4)

    @pytest.mark.parametrize("sample_idx, expected", [
        (0, 1228.0),
    ])
    def test_dist_end_point(self, sample_idx, expected):
        samples = ExxonMapper(self.record).sub_samples

        if expected is None:
            assert samples[sample_idx].distillation_data.end_point is None
        else:
            end_point = samples[sample_idx].distillation_data.end_point

            assert isclose(end_point.value, expected, rel_tol=1e-4)
            assert end_point.unit == 'F'

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
