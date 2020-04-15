'''
    tests of the Environment Canada data import modules

    As complete as possible, because we want to test for correctness,
    and we also want to document how it works.
    Either we test it correctly, or we test it in an episodic manner on the
    real dataset.
'''
from pathlib import Path

import pytest

from oil_database.data_sources.noaa_fm import (OilLibraryCsvFile,
                                               OilLibraryRecordParser,
                                               OilLibraryAttributeMapper,
                                               ImportFileHeaderLengthError)

from pprint import pprint

import pdb

example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"
data_file = example_dir / "OilLibTestSet.txt"


class TestOilLibraryCsvFile:
    def test_init(self):
        with pytest.raises(TypeError):
            _reader = OilLibraryCsvFile()

    def test_init_nonexistant_file(self):
        with pytest.raises(FileNotFoundError):
            _reader = OilLibraryCsvFile('bogus.file')

    def test_init_invalid_file(self):
        with pytest.raises(ImportFileHeaderLengthError):
            _reader = OilLibraryCsvFile(example_index)

    def test_init_with_valid_file(self):
        reader = OilLibraryCsvFile(data_file)

        assert reader.name == data_file

        assert reader.num_columns == 159
        assert len(reader.file_columns) == 159
        assert len(reader.file_columns_lu.keys()) == 159

        # There are over a hundred fields here, so let's just check
        # some of the individual category/field combinations
        assert reader.file_columns_lu['Oil_Name'] == 0
        assert reader.file_columns_lu['K0Y'] == 158

    def test_get_records(self):
        reader = OilLibraryCsvFile(data_file)

        recs = list(reader.get_records())

        # records in our test file
        assert len(recs) == 1495

        for r in recs:
            # each item coming from records() is a dict with field keys and
            # data
            assert len(r) == 159

    @pytest.mark.parametrize('oil_id, field, expected', [
        ('AD00009', 'Oil_Name', 'ABU SAFAH'),
        ('AD00009', 'K0Y', 2.02e-06),
        pytest.param('NotHere', 'Oil_Name', None,
                     marks=pytest.mark.raises(exception=KeyError)),
    ])
    def test_get_record(self, oil_id, field, expected):
        '''
            There are over a hundred fields here, so let's just check
            some of the individual fields/values.

            Note: Should we allow non-existing oil_id's in get_record
        '''
        reader = OilLibraryCsvFile(data_file)

        rec = reader.get_record(oil_id)

        print(rec)

        assert rec[field] == expected


class TestOilLibraryRecordParser:
    reader = OilLibraryCsvFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _parser = OilLibraryRecordParser()

    def test_init_invalid(self):
        with pytest.raises(AttributeError):
            _parser = OilLibraryRecordParser(None, None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('AD00009', 1993),
        pytest.param('AD00269', 2017,
                     marks=pytest.mark.raises(exception=TypeError)),
    ])
    def test_init_valid_data(self, oil_id, expected):
        '''
            We are being fairly light on the parameter checking in our
            constructor.  So if no file props are passed in, we can still
            construct the parser, but accessing reference_date could raise
            a TypeError.
            This is because the reference_date will sometimes need the
            file props if the reference field contains no date information.
        '''
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(rec, None)  # should construct fine

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('oil_id, expected', [
        ('AD00009', 1993),
        ('AD00269', 2017),
    ])
    def test_init_valid_data_and_file_props(self, oil_id, expected):
        '''
            The reference_date will sometimes need the file props if the
            reference field contains no date information.  check that the
            file props are correctly parsed.
        '''
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(rec, self.reader.file_props)

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('label, expected', [
        ('A Label', 'a_label'),
        ('0.0', '_0_0'),
        ('Density 5 ̊C (g/mL)', 'density_5_c_g_ml'),
        ('14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)',
         '_14ss_h_17ss_h_20_ethylcholestane_c29assss'),
    ])
    def test_slugify(self, label, expected):
        rec = self.reader.get_record('AD00009')
        parser = OilLibraryRecordParser(rec, self.reader.file_props)

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('AD00009', 'oil_name', 'ABU SAFAH'),
        ('AD00009', 'oil_id', 'AD00009'),
        ('AD00009', 'location', 'SAUDI ARABIA'),
        ('AD00009', 'field_name', 'ABU SAFAH'),
        ('AD00009', 'product_type', 'crude'),
        ('AD00025', 'product_type', 'refined'),
        ('AD00005', 'synonyms', [{'name': 'ABSORBENT OIL'}]),
        ('AD00009', 'reference', {'reference': ('Williams, R., ARAMCO, Letter '
                                                'to Lehr, W.,  NOAA, '
                                                'March 13, 1993.'),
                                  'year': 1993}),
        ('AD00269', 'reference', {'reference': ('Drift River Terminal, '
                                                'Anchorage, AK.  Memo to '
                                                'John Whitney, NOAA.'),
                                  'year': 2017}),
        ('AD00010', 'comments', ('Crude sample represents 1989 winter '
                                 'production.  Product considered an '
                                 'Arabian medium crude.')
         ),
        ('AD00009', 'api', 28.0),
        ('AD00009', 'pour_point_min_k', 244.0),
        ('AD00009', 'pour_point_max_k', 244.0),
        ('AD00047', 'pour_point_min_k', None),  # '<' sign in field
        ('AD00047', 'pour_point_max_k', 293.0),
        ('AD01598', 'pour_point_min_k', 323.0),  # '>' sign in field
        ('AD01598', 'pour_point_max_k', None),
        ('AD00025', 'asphaltenes', 0.02),
        ('AD00025', 'aromatics', 0.128),
        ('AD00025', 'wax_content', 0.069),
        ('AD00025', 'water_content_emulsion', 0.9),
        ('AD00025', 'emuls_constant_min', 0.148),
        ('AD00025', 'emuls_constant_max', 0.255),
        ('AD00025', 'flash_point_min_k', 280.0),
        ('AD00025', 'flash_point_max_k', 280.0),
        ('AD00125', 'flash_point_min_k', None),  # '<' sign in field
        ('AD00125', 'flash_point_max_k', 230.0),
        ('AD00135', 'flash_point_min_k', 363.15),  # '>' sign in field
        ('AD00135', 'flash_point_max_k', None),
        ('AD00020', 'densities', [
            {'kg_m_3': 904.0, 'ref_temp_k': 273.0},
            {'kg_m_3': 920.0, 'ref_temp_k': 273.0, 'weathering': 0.09},
            {'kg_m_3': 934.0, 'ref_temp_k': 273.0, 'weathering': 0.16}
         ]),
        ('AD02068', 'kvis', [
            {'m_2_s': 3e-06, 'ref_temp_k': 273.0},
            {'m_2_s': 2e-06, 'ref_temp_k': 288.0},
            {'m_2_s': 4e-06, 'ref_temp_k': 273.0, 'weathering': 0.11},
            {'m_2_s': 3e-06, 'ref_temp_k': 288.0, 'weathering': 0.11},
            {'m_2_s': 7e-06, 'ref_temp_k': 273.0, 'weathering': 0.26},
            {'m_2_s': 5e-06, 'ref_temp_k': 288.0, 'weathering': 0.26}
         ]),
        ('AD01987', 'dvis', [
            {'kg_ms': 0.034, 'ref_temp_k': 273.0},
            {'kg_ms': 0.016, 'ref_temp_k': 288.0},
            {'kg_ms': 5.66, 'ref_temp_k': 273.0, 'weathering': 0.31},
            {'kg_ms': 0.9, 'ref_temp_k': 288.0, 'weathering': 0.31}
         ]),
        ('AD00025', 'cuts', [
            {'fraction': 0.01, 'liquid_temp_k': 115.0, 'vapor_temp_k': 37.0},
            {'fraction': 0.05, 'liquid_temp_k': 158.0, 'vapor_temp_k': 95.0},
            {'fraction': 0.1, 'liquid_temp_k': 182.0, 'vapor_temp_k': 111.0},
            {'fraction': 0.15, 'liquid_temp_k': 206.0, 'vapor_temp_k': 126.0},
            {'fraction': 0.2, 'liquid_temp_k': 234.0, 'vapor_temp_k': 142.0},
            {'fraction': 0.25, 'liquid_temp_k': 260.0, 'vapor_temp_k': 155.0},
            {'fraction': 0.3, 'liquid_temp_k': 286.0, 'vapor_temp_k': 189.0},
            {'fraction': 0.34, 'liquid_temp_k': 304.0, 'vapor_temp_k': 213.0}
         ]),
        ('AD00025', 'toxicities', [
            {'after_48h': 1.12, 'species': 'Daphia Magna', 'tox_type': 'EC'},
            {'after_24h': 8.17, 'species': 'Artemia spp.', 'tox_type': 'EC'},
            {'after_48h': 6.28, 'species': 'Daphia Magna', 'tox_type': 'LC'},
            {'after_24h': 10.6, 'species': 'Artemia spp.', 'tox_type': 'LC'}
         ]),
        ('AD00025', 'ifts', [
            {'interface': 'water', 'n_m': 0.0215, 'ref_temp_k': 288.0},
            {'interface': 'seawater', 'n_m': 0.015, 'ref_temp_k': 288.0}
         ]),
        ('AD00025', 'cut_units', 'weight'),
        ('AD00025', 'oil_class', 'group 2'),
        ('AD00020', 'adhesion', 0.28),
        ('AD00020', 'adhesion', 0.28),
        ('AD00084', 'benzene', 0.05),
        ('AD01500', 'naphthenes', 0.0004),
        ('AD00024', 'paraffins', 0.783),
        ('AD00025', 'polars', 0.012),
        ('AD00017', 'resins', 0.01),
        ('AD00017', 'saturates', 0.8),
        ('AD00020', 'sulphur', 0.0104),
        ('AD00020', 'reid_vapor_pressure', 0.19),
        ('AD00020', 'viscosity_multiplier', None),  # all fields blank
        ('AD00020', 'nickel', 14.7),  # percent??  ppm??
        ('AD00020', 'vanadium', 33.9),  # percent??  ppm??
        ('AD01853', 'conrandson_residuum', 0.0019),
        ('AD01901', 'conrandson_crude', 0.0054),
        ('AD00020', 'dispersability_temp_k', 280.0),
        ('AD00020', 'preferred_oils', True),
        ('AD00020', 'k0y', 0.00000202),
        ('AD01987', 'weathering', {0.0, 0.31}),
        ('AD02068', 'weathering', {0.0, 0.11, 0.26}),
    ])
    def test_attrs(self, oil_id, attr, expected):
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(rec, self.reader.file_props)

        pprint(getattr(parser, attr))
        assert getattr(parser, attr) == expected
