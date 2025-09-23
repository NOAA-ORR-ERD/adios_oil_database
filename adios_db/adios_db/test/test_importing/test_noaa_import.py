import os
from pathlib import Path
import json

import pytest

dateutil = pytest.importorskip("dateutil")

import adios_db
try: # can't work if dateutil isn't there
    from adios_db.data_sources.noaa_fm import (OilLibraryCsvFile,
                                           OilLibraryRecordParser,
                                           OilLibraryAttributeMapper,
                                           ImportFileHeaderLengthError)
except:
    pass

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing

example_dir = Path(__file__).resolve().parent / 'example_data'
example_index = example_dir / 'index.txt'
data_file = example_dir / 'OilLibTestSet.txt'


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
        assert len(recs) == 20

        for rec, file_props in recs:
            # each item coming from records() is a list containing 2 dicts.
            # - dict with field keys & data representing the record data
            # - dict with keys & data representing the properties of the
            #   source data file
            assert len(rec) == 159
            assert len(file_props) == 3

    @pytest.mark.parametrize('oil_id, field, expected', [
        ('AD00009', 'Oil_Name', 'ABU SAFAH'),
        ('AD00009', 'K0Y', 2.02e-06),
        pytest.param('NotHere', 'Oil_Name', None,
                     marks=pytest.mark.raises(exception=KeyError)),
    ])
    def test_get_record(self, oil_id, field, expected):
        """
        There are over a hundred fields here, so let's just check
        some of the individual fields/values.

        Note: Should we allow non-existing oil_id's in get_record
        """
        reader = OilLibraryCsvFile(data_file)
        rec, file_props = reader.get_record(oil_id)

        assert type(file_props) == dict
        assert len(file_props) == 3
        assert set(file_props.keys()) == {'version', 'created', 'application'}

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
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if no file props are passed in, we can still
        construct the parser, but accessing reference_date could raise
        a TypeError.
        This is because the reference_date will sometimes need the
        file props if the reference field contains no date information.
        """
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(rec[0], None)  # should construct fine

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('oil_id, expected', [
        ('AD00009', 1993),
        ('AD00269', 2017),
    ])
    def test_init_valid_data_and_file_props(self, oil_id, expected):
        """
        The reference_date will sometimes need the file props if the
        reference field contains no date information.  check that the
        file props are correctly parsed.
        """
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(*rec)

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
        parser = OilLibraryRecordParser(*rec)

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('AD00009', 'oil_name', 'ABU SAFAH'),
        ('AD00009', 'oil_id', 'AD00009'),
        ('AD00009', 'location', 'SAUDI ARABIA'),
        ('AD00009', 'field_name', 'ABU SAFAH'),
        ('AD00009', 'product_type', 'Crude Oil NOS'),
        ('AD00025', 'product_type', 'Refined Product NOS'),
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
        ('AD00009', 'pour_point', {'measurement': {'value': 244.0,
                                                   'unit': 'K'}}),
        ('AD00047', 'pour_point', {'measurement': {'max_value': 293.0,
                                                   'min_value': None,
                                                   'unit': 'K'}}),
        ('AD01598', 'pour_point', {'measurement': {'max_value': None,
                                                   'min_value': 323.0,
                                                   'unit': 'K'}}),
        ('AD00005', 'pour_point', None),
        ('AD00025', 'flash_point_min_k', 280.0),
        ('AD00025', 'flash_point_max_k', 280.0),
        ('AD00125', 'flash_point_min_k', None),  # '<' sign in field
        ('AD00125', 'flash_point_max_k', 230.0),
        ('AD00135', 'flash_point_min_k', 363.15),  # '>' sign in field
        ('AD00135', 'flash_point_max_k', None),
        ('AD00025', 'flash_point', {'measurement': {'value': 280.0,
                                                    'unit': 'K'}}),
        ('AD00125', 'flash_point', {'measurement': {'max_value': 230.0,
                                                    'min_value': None,
                                                    'unit': 'K'}}),
        ('AD00020', 'flash_point', None),
        ('AD00025', 'wax_content', 0.069),
        ('AD00025', 'water_content_emulsion', 0.9),
        ('AD00025', 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.0},
             'weathering': 0.148},
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.9},
             'weathering': 0.255}
         ]),
        ('AD00025', 'emuls_constant_min', 0.148),
        ('AD00025', 'emuls_constant_max', 0.255),
        ('AD00020', 'densities', [
            {'density': {'value': 904.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'density': {'value': 920.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.09},
            {'density': {'value': 934.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.16},
         ]),
        ('AD02068', 'kinematic_viscosities', [
            {'viscosity': {'value': 3e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 2e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 4e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.11},
            {'viscosity': {'value': 3e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.11},
            {'viscosity': {'value': 7e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.26},
            {'viscosity': {'value': 5e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.26},
         ]),
        ('AD01987', 'dynamic_viscosities', [
            {'viscosity': {'value': 0.034, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 0.016, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 5.66, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.31},
            {'viscosity': {'value': 0.9, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.31},
         ]),
        ('AD00025', 'cuts', [
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.01},
             'liquid_temp': {'unit': 'K', 'value': 115.0},
             'vapor_temp': {'unit': 'K', 'value': 37.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.05},
             'liquid_temp': {'unit': 'K', 'value': 158.0},
             'vapor_temp': {'unit': 'K', 'value': 95.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.1},
             'liquid_temp': {'unit': 'K', 'value': 182.0},
             'vapor_temp': {'unit': 'K', 'value': 111.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.15},
             'liquid_temp': {'unit': 'K', 'value': 206.0},
             'vapor_temp': {'unit': 'K', 'value': 126.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.2},
             'liquid_temp': {'unit': 'K', 'value': 234.0},
             'vapor_temp': {'unit': 'K', 'value': 142.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.25},
             'liquid_temp': {'unit': 'K', 'value': 260.0},
             'vapor_temp': {'unit': 'K', 'value': 155.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.3},
             'liquid_temp': {'unit': 'K', 'value': 286.0},
             'vapor_temp': {'unit': 'K', 'value': 189.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                          'value': 0.34},
             'liquid_temp': {'unit': 'K', 'value': 304.0},
             'vapor_temp': {'unit': 'K', 'value': 213.0}}
         ]),
        ('AD00038', 'cuts', [
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.05},
             'vapor_temp': {'unit': 'K', 'value': 302.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.1},
             'vapor_temp': {'unit': 'K', 'value': 342.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.15},
             'vapor_temp': {'unit': 'K', 'value': 373.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.2},
             'vapor_temp': {'unit': 'K', 'value': 401.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.25},
             'vapor_temp': {'unit': 'K', 'value': 424.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.3},
             'vapor_temp': {'unit': 'K', 'value': 445.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.35},
             'vapor_temp': {'unit': 'K', 'value': 471.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.4},
             'vapor_temp': {'unit': 'K', 'value': 486.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.45},
             'vapor_temp': {'unit': 'K', 'value': 511.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.5},
             'vapor_temp': {'unit': 'K', 'value': 534.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.55},
             'vapor_temp': {'unit': 'K', 'value': 555.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.6},
             'vapor_temp': {'unit': 'K', 'value': 577.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.65},
             'vapor_temp': {'unit': 'K', 'value': 602.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.7},
             'vapor_temp': {'unit': 'K', 'value': 624.0}},
            {'fraction': {'unit': 'fraction', 'unit_type': 'volumefraction',
                          'value': 0.75},
             'vapor_temp': {'unit': 'K', 'value': 646.0}}
         ]),
        ('AD00025', 'toxicities', [
            {'after_48h': 1.12, 'species': 'Daphia Magna', 'tox_type': 'EC'},
            {'after_24h': 8.17, 'species': 'Artemia spp.', 'tox_type': 'EC'},
            {'after_48h': 6.28, 'species': 'Daphia Magna', 'tox_type': 'LC'},
            {'after_24h': 10.6, 'species': 'Artemia spp.', 'tox_type': 'LC'}
         ]),
        ('AD00025', 'interfacial_tensions', [
            {'interface': 'water',
             'method': None,
             'tension': {'value': 0.0215, 'unit': 'N/m'},
             'ref_temp': {'value': 288.0, 'unit': 'K'}
             },
            {'interface': 'seawater',
             'method': None,
             'tension': {'value': 0.015, 'unit': 'N/m'},
             'ref_temp': {'value': 288.0, 'unit': 'K'}
             },
         ]),
        ('AD00025', 'cut_units', 'weight'),
        ('AD00025', 'oil_class', 'group 2'),
        ('AD00020', 'adhesion', 0.28),
        ('AD00020', 'adhesion', 0.28),
        ('AD00084', 'benzene', 0.05),
        ('AD01500', 'naphthenes', 0.0004),
        ('AD00024', 'paraffins', 0.783),
        ('AD00025', 'polars', 0.012),
        ('AD00017', 'saturates', 0.8),
        ('AD00025', 'aromatics', 0.128),
        ('AD00017', 'resins', 0.01),
        ('AD00025', 'asphaltenes', 0.02),
        ('AD00020', 'sulphur', 0.0104),
        ('AD00020', 'reid_vapor_pressure', 0.19),
        ('AD00020', 'viscosity_multiplier', None),  # all fields blank
        ('AD00020', 'nickel', 14.7),  # percent??  ppm??
        ('AD00020', 'vanadium', 33.9),  # percent??  ppm??
        ('AD01853', 'conrandson_residuum', 0.0019),
        ('AD01901', 'conrandson_crude', 0.0054),
        ('AD01853', 'conradson', {
            'residue': {'value': 0.0019, 'unit': 'fraction'},
         }),
        ('AD01901', 'conradson', {
            'crude': {'value': 0.0054, 'unit': 'fraction'},
         }),
        ('AD00025', 'conradson', None),
        ('AD00020', 'dispersability_temp_k', 280.0),  # where would this go?
        ('AD00020', 'preferred_oils', True),
        ('AD00020', 'k0y', 0.00000202),
        ('AD00017', 'SARA', {
            'aromatics': {'value': 0.19, 'unit': 'fraction'},
            'asphaltenes': {'value': 0.01, 'unit': 'fraction'},
            'resins': {'value': 0.01, 'unit': 'fraction'},
            'saturates': {'value': 0.8, 'unit': 'fraction'},
         }),
        ('AD00025', 'SARA', {
            'aromatics': {'value': 0.128, 'unit': 'fraction'},
            'asphaltenes': {'value': 0.02, 'unit': 'fraction'},
            'saturates': {'value': 0.842, 'unit': 'fraction'},
         }),
        ('AD00005', 'SARA', None),
        ('AD00025', 'weathering', [0.0, 0.148, 0.255]),
        ('AD01987', 'weathering', [0.0, 0.31]),
        ('AD02068', 'weathering', [0.0, 0.11, 0.26]),
    ])
    def test_attrs(self, oil_id, attr, expected):
        rec = self.reader.get_record(oil_id)
        parser = OilLibraryRecordParser(*rec)

        assert getattr(parser, attr) == expected


class TestOilLibraryAttributeMapper:
    reader = OilLibraryCsvFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = OilLibraryAttributeMapper()

    def test_init_invalid(self):
        """
        This should construct just fine.  Of course nothing will really
        work if you pass in a None value.
        """
        _mapper = OilLibraryAttributeMapper(None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('AD00009', 1993),
    ])
    def test_init_valid_data(self, oil_id, expected):
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if no file props are passed in, we can still
        construct the parser, but accessing reference_date could raise
        a TypeError.
        This is because the reference_date will sometimes need the
        file props if the reference field contains no date information.
        """
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))

        assert mapper.reference['year'] == expected

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('AD00009', '_id', 'AD00009'),
        ('AD00009', 'oil_id', 'AD00009'),
        ('AD00009', 'name', 'ABU SAFAH'),
        ('AD00009', 'location', 'SAUDI ARABIA'),
        ('AD00009', 'reference', {'reference': ('Williams, R., ARAMCO, Letter '
                                                'to Lehr, W.,  NOAA, '
                                                'March 13, 1993.'),
                                  'year': 1993}),
        ('AD00010', 'comments', ('Crude sample represents 1989 winter '
                                 'production.  Product considered an '
                                 'Arabian medium crude.')
         ),
        ('AD00009', 'labels', []),
        ('AD00009', 'product_type', 'Crude Oil NOS'),
        ('AD00009', 'API', 28.0),
        ('AD00009', 'status', None),
        # ('AD00009', 'sub_samples', None),  # we'll test this later
        ('AD00020', 'densities', [
            {'density': {'value': 904.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'density': {'value': 920.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.09},
            {'density': {'value': 934.0, 'unit': 'kg/m^3'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.16},
         ]),
        ('AD01987', 'dynamic_viscosities', [
            {'viscosity': {'value': 0.034, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 0.016, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 5.66, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.31},
            {'viscosity': {'value': 0.9, 'unit': 'kg/(m s)'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.31},
         ]),
        ('AD02068', 'kinematic_viscosities', [
            {'viscosity': {'value': 3e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 2e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.0},
            {'viscosity': {'value': 4e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.11},
            {'viscosity': {'value': 3e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.11},
            {'viscosity': {'value': 7e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 273.0, 'unit': 'K'},
             'weathering': 0.26},
            {'viscosity': {'value': 5e-06, 'unit': 'm^2/s'},
             'ref_temp': {'value': 288.0, 'unit': 'K'},
             'weathering': 0.26},
         ]),
        ('AD00025', 'interfacial_tensions', [
            {'interface': 'water',
             'method': None,
             'tension': {'value': 0.0215, 'unit': 'N/m'},
             'ref_temp': {'value': 288.0, 'unit': 'K'}
             },
            {'interface': 'seawater',
             'method': None,
             'tension': {'value': 0.015, 'unit': 'N/m'},
             'ref_temp': {'value': 288.0, 'unit': 'K'}
             },
         ]),
        ('AD00009', 'pour_point', {'measurement': {'value': 244.0,
                                                   'unit': 'K'}}),
        ('AD00047', 'pour_point', {'measurement': {'max_value': 293.0,
                                                   'min_value': None,
                                                   'unit': 'K'}}),
        ('AD01598', 'pour_point', {'measurement': {'max_value': None,
                                                   'min_value': 323.0,
                                                   'unit': 'K'}}),
        ('AD00005', 'pour_point', None),
        ('AD00025', 'flash_point', {'measurement': {'value': 280.0,
                                                    'unit': 'K'}}),
        ('AD00125', 'flash_point', {'measurement': {'max_value': 230.0,
                                                    'min_value': None,
                                                    'unit': 'K'}}),
        ('AD00020', 'flash_point', None),
        ('AD00025', 'distillation_data', {
            'type': 'mass fraction',
            'cuts': [
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.01},
                 'liquid_temp': {'unit': 'K', 'value': 115.0},
                 'vapor_temp': {'unit': 'K', 'value': 37.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.05},
                 'liquid_temp': {'unit': 'K', 'value': 158.0},
                 'vapor_temp': {'unit': 'K', 'value': 95.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.1},
                 'liquid_temp': {'unit': 'K', 'value': 182.0},
                 'vapor_temp': {'unit': 'K', 'value': 111.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.15},
                 'liquid_temp': {'unit': 'K', 'value': 206.0},
                 'vapor_temp': {'unit': 'K', 'value': 126.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.2},
                 'liquid_temp': {'unit': 'K', 'value': 234.0},
                 'vapor_temp': {'unit': 'K', 'value': 142.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.25},
                 'liquid_temp': {'unit': 'K', 'value': 260.0},
                 'vapor_temp': {'unit': 'K', 'value': 155.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.3},
                 'liquid_temp': {'unit': 'K', 'value': 286.0},
                 'vapor_temp': {'unit': 'K', 'value': 189.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.34},
                 'liquid_temp': {'unit': 'K', 'value': 304.0},
                 'vapor_temp': {'unit': 'K', 'value': 213.0}}],
        }),
        ('AD00025', 'toxicities', [
            {'after_48h': 1.12, 'species': 'Daphia Magna', 'tox_type': 'EC'},
            {'after_24h': 8.17, 'species': 'Artemia spp.', 'tox_type': 'EC'},
            {'after_48h': 6.28, 'species': 'Daphia Magna', 'tox_type': 'LC'},
            {'after_24h': 10.6, 'species': 'Artemia spp.', 'tox_type': 'LC'}
         ]),
        ('AD00020', 'adhesion', {'unit': 'N/m^2', 'value': 0.28}),
        ('AD00025', 'adhesion', None),
     ])
    def test_attrs(self, oil_id, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))

        assert getattr(mapper, attr) == expected

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('AD00009', 'name', 'ABU SAFAH'),
        ('AD00009', 'source_id', 'AD00009'),
        ('AD00009', 'location', 'SAUDI ARABIA'),
        ('AD00009', 'reference', {'reference': ('Williams, R., ARAMCO, Letter '
                                                'to Lehr, W.,  NOAA, '
                                                'March 13, 1993.'),
                                  'year': 1993}),
        ('AD00010', 'comments', ('Crude sample represents 1989 winter '
                                 'production.  Product considered an '
                                 'Arabian medium crude.')
         ),
        ('AD00009', 'product_type', 'Crude Oil NOS'),
        ('AD00009', 'API', 28.0),
    ])
    def test_metadata(self, oil_id, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        meta = mapper.metadata

        assert meta[attr] == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('AD02068', 0, 'name', 'Fresh Oil Sample'),
        ('AD02068', -1, 'name', '26.0% Evaporated'),
        ('AD02068', 0, 'short_name', 'Fresh Oil'),
        ('AD02068', -1, 'short_name', '26.0% Evaporated'),
        ('AD02068', 0, 'fraction_weathered', {'unit': 'fraction',
                                              'value': 0.0}),
        ('AD02068', -1, 'fraction_weathered', {'unit': 'fraction',
                                               'value': 0.26}),
        ('AD02068', 0, 'boiling_point_range', None),
        ('AD02068', -1, 'boiling_point_range', None),
        ('AD02068', -1, 'boiling_point_range', None),
    ])
    def test_sample_metadata_attribute(self, oil_id, index, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        sample = mapper.sub_samples[index]['metadata']

        assert sample[attr] == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        # properties without weathering are fresh, so only show up in the
        # first sample
        ('AD02068', 0, 'pour_point', {'measurement': {'unit': 'K',
                                                      'value': 243.0}}),
        ('AD02068', 0, 'flash_point', {'measurement': {'unit': 'K',
                                                       'value': 305.0}}),
        pytest.param('AD01998', 1, 'pour_point', None,
                     marks=pytest.mark.raises(exception=KeyError)),
        pytest.param('AD01998', 1, 'flash_point', None,
                     marks=pytest.mark.raises(exception=KeyError)),
        ('AD00025', 0, 'interfacial_tension_water', [
            {'method': None,
             'ref_temp': {'unit': 'K', 'value': 288.0},
             'tension': {'unit': 'N/m', 'value': 0.0215}}
         ]),
        ('AD00025', 0, 'interfacial_tension_seawater', [
            {'method': None,
             'ref_temp': {'unit': 'K', 'value': 288.0},
             'tension': {'unit': 'N/m', 'value': 0.015}}
         ]),
        pytest.param('AD01998', 1, 'interfacial_tensions', None,
                     marks=pytest.mark.raises(exception=KeyError)),
        # weathered properties will show up in multiple samples
        ('AD02068', 0, 'densities', [
            {'density': {'unit': 'kg/m^3', 'value': 800.0},
             'ref_temp': {'unit': 'K', 'value': 273.0}},
            {'density': {'unit': 'kg/m^3', 'value': 790.0},
             'ref_temp': {'unit': 'K', 'value': 288.0}}
         ]),
        ('AD02068', 1, 'densities', [
            {'density': {'unit': 'kg/m^3', 'value': 815.0},
             'ref_temp': {'unit': 'K', 'value': 273.0}},
            {'density': {'unit': 'kg/m^3', 'value': 805.0},
             'ref_temp': {'unit': 'K', 'value': 288.0}}
         ]),
        ('AD02068', 2, 'kinematic_viscosities', [
            {'ref_temp': {'unit': 'K', 'value': 273.0},
             'viscosity': {'unit': 'm^2/s', 'value': 7e-06}},
            {'ref_temp': {'unit': 'K', 'value': 288.0},
             'viscosity': {'unit': 'm^2/s', 'value': 5e-06}}
         ]),
        ('AD01998', 0, 'dynamic_viscosities', [
            {'ref_temp': {'unit': 'K', 'value': 273.0},
             'viscosity': {'unit': 'kg/(m s)', 'value': 0.025}},
            {'ref_temp': {'unit': 'K', 'value': 288.0},
             'viscosity': {'unit': 'kg/(m s)', 'value': 0.014}}
         ]),
        ('AD01998', 2, 'dynamic_viscosities', [
            {'ref_temp': {'unit': 'K', 'value': 273.0},
             'viscosity': {'unit': 'kg/(m s)', 'value': 0.068}},
            {'ref_temp': {'unit': 'K', 'value': 288.0},
             'viscosity': {'unit': 'kg/(m s)', 'value': 0.032}}
         ]),
    ])
    def test_physical_properties(self, oil_id, index, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        phys = mapper.sub_samples[index]['physical_properties']

        assert phys[attr] == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('AD00010', 0, 'emulsions', None),
        ('AD00017', 0, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.71}}
         ]),
        ('AD00020', 0, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.89}}
         ]),
        ('AD00025', 1, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.0}}
         ]),
        ('AD00025', 2, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.9}}
         ]),
        ('AD00025', -1, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0.0},
             'ref_temp': {'unit': 'K', 'value': 288.15},
             'water_content': {'unit': 'fraction', 'value': 0.9}}
         ]),
    ])
    def test_environmental_behavior(self, oil_id, index, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        environ = mapper.sub_samples[index]['environmental_behavior']

        if expected is None:
            assert attr not in environ
        else:
            assert environ[attr] == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('AD00017', 0, 'saturates', {'unit': 'fraction', 'value': 0.8}),
        ('AD00017', 0, 'aromatics', {'unit': 'fraction', 'value': 0.19}),
        ('AD00017', 0, 'resins', {'unit': 'fraction', 'value': 0.01}),
        ('AD00017', 0, 'asphaltenes', {'unit': 'fraction', 'value': 0.01}),
    ])
    def test_sara(self, oil_id, index, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        environ = mapper.sub_samples[index]['SARA']

        assert environ[attr] == expected

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('AD00025', 0, {
            'type': 'mass fraction',
            'cuts': [
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.01},
                 'liquid_temp': {'unit': 'K', 'value': 115.0},
                 'vapor_temp': {'unit': 'K', 'value': 37.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.05},
                 'liquid_temp': {'unit': 'K', 'value': 158.0},
                 'vapor_temp': {'unit': 'K', 'value': 95.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.1},
                 'liquid_temp': {'unit': 'K', 'value': 182.0},
                 'vapor_temp': {'unit': 'K', 'value': 111.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.15},
                 'liquid_temp': {'unit': 'K', 'value': 206.0},
                 'vapor_temp': {'unit': 'K', 'value': 126.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.2},
                 'liquid_temp': {'unit': 'K', 'value': 234.0},
                 'vapor_temp': {'unit': 'K', 'value': 142.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.25},
                 'liquid_temp': {'unit': 'K', 'value': 260.0},
                 'vapor_temp': {'unit': 'K', 'value': 155.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.3},
                 'liquid_temp': {'unit': 'K', 'value': 286.0},
                 'vapor_temp': {'unit': 'K', 'value': 189.0}},
                {'fraction': {'unit': 'fraction', 'unit_type': 'massfraction',
                              'value': 0.34},
                 'liquid_temp': {'unit': 'K', 'value': 304.0},
                 'vapor_temp': {'unit': 'K', 'value': 213.0}}],
        }),
        ('AD00020', 0, {'cuts': [], 'type': 'mass fraction'}),
    ])
    def test_distillation_data(self, oil_id, index, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        dist = mapper.sub_samples[index]['distillation_data']

        assert dist == expected

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('AD00025', 0, {
            'names': set()
         }),
        ('AD00084', 0, {
            'names': {'benzene', }
         }),
    ])
    def test_compounds(self, oil_id, index, expected):
        """
        Data points that are classified as compounds:
        - benzene
        """
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        compounds = mapper.sub_samples[index]['compounds']

        for c in compounds:
            assert 'name' in c
            assert 'measurement' in c

        assert set([c['name'] for c in compounds]) == expected['names']

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('AD00020', 0, {
            'names': {'water_content', 'wax_content',
                      'sulfur', 'nickel', 'vanadium'}
         }),
        ('AD00024', 0, {
            'names': {'paraffins', 'polars', 'wax_content'}
         }),
        ('AD01500', 0, {
            'names': {'naphthenes', }
         }),
    ])
    def test_bulk_composition(self, oil_id, index, expected):
        """
        Data points that are classified in bulk composition:
        - Water Content Emulsion
        - Wax Content
        - Sulphur
        - Naphthenes
        - Paraffins
        - Nickel
        - Vanadium
        - Polars
        """
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        composition = mapper.sub_samples[index]['bulk_composition']

        for c in composition:
            assert 'name' in c
            assert 'measurement' in c

        assert set([c['name'] for c in composition]) == expected['names']

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('AD01901', 0, {
            'names': {'Conradson Carbon Residue (CCR)'}
         }),
        ('AD01853', 0, {
            'names': {'Reid Vapor Pressure', 'Conradson Residuum'}
         }),
    ])
    def test_industry_properties(self, oil_id, index, expected):
        """
        Data points that are classified in industry properties:
        - Reid Vapor Pressure
        - Conradson Crude
        - Conradson Residuum
        """
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        composition = mapper.sub_samples[index]['industry_properties']

        for c in composition:
            assert 'name' in c
            assert 'measurement' in c

        assert set([c['name'] for c in composition]) == expected['names']

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('AD00020', 0, 'name', 'Fresh Oil Sample'),
        ('AD00005', 0, 'name', 'Fresh Oil Sample'),
    ])
    def test_py_json(self, oil_id, index, attr, expected):
        rec = self.reader.get_record(oil_id)
        mapper = OilLibraryAttributeMapper(OilLibraryRecordParser(*rec))
        oil = mapper.py_json()
        sample = oil['sub_samples'][index]

        assert sample['metadata'][attr] == expected

    def test_save_to_json(self):
        """
        Save an example .json file.  This is not so much a test, but a job
        to provide sample data that people can look at.
        """
        parser = OilLibraryRecordParser(*self.reader.get_record('AD00025'))
        mapper = OilLibraryAttributeMapper(parser)
        py_json = mapper.py_json()

        py_json['status'] = []

        filename = 'AD-Example-Record.json'
        file_path = os.path.sep.join(
            adios_db.__file__.split(os.path.sep)[:-3] + ['examples', filename]
        )

        print(f'saving to: {file_path}')
        with open(file_path, 'w', encoding="utf-8") as fd:
            json.dump(py_json, fd, indent=4, sort_keys=True)
