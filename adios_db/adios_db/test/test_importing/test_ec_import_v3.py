"""
tests of the Environment Canada data import modules

As complete as possible, because we want to test for correctness,
and we also want to document how it works.
Either we test it correctly, or we test it in an episodic manner on the
real dataset.
"""
import pytest

try:
    from slugify import Slugify
    import dateutil
except ImportError:
    pytest.skip(
        'You need the awesome slugify and dateutil packages '
        'to run these tests',
        allow_module_level=True
    )

import os
from pathlib import Path
import json

import numpy as np

import adios_db
from adios_db.data_sources.env_canada.v3 import (EnvCanadaCsvFile1999,
                                                 EnvCanadaCsvRecordParser1999,
                                                 EnvCanadaCsvRecordMapper1999,
                                                 reference_codes)

from adios_db.data_sources.env_canada.v2 import InvalidFileError

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing


example_dir = Path(__file__).resolve().parent / 'example_data'
example_index = example_dir / 'index.txt'
data_file = example_dir / 'ECCC_AlaskaNorthSlope.csv'


class TestEnvCanadaReferenceCodes(object):
    def test_init(self):
        print(f'reference_codes: {type(reference_codes)}')

        assert isinstance(reference_codes, dict)

        # Check that we parsed the first and last reference codes in each page
        # of the document
        assert [k in reference_codes
                for k in ('ACGIH 96', 'ASTM D4814',
                          'Bobra 83', 'Dukek 78',
                          'ESD', 'Mackay 82b',
                          'MacLean 89', 'OGJ 83g',
                          'OGJ 83h', 'OGJ 91d',
                          'OGJ 91e', 'OGJ 94f',
                          'OGJ 95a', 'Ross 99b',
                          'Rossi 76 ', 'Walton 93')]


class TestEnvCanadaCsvFile(object):
    def test_init(self):
        with pytest.raises(TypeError):
            _reader = EnvCanadaCsvFile1999()

    def test_init_nonexistant_file(self):
        with pytest.raises(FileNotFoundError):
            _reader = EnvCanadaCsvFile1999('bogus.file')

    def test_init_invalid_file(self):
        with pytest.raises(InvalidFileError):
            _reader = EnvCanadaCsvFile1999(example_index)

    def test_init_with_valid_file(self):
        reader = EnvCanadaCsvFile1999(data_file)

        assert reader.name == data_file

    def test_get_records(self):
        reader = EnvCanadaCsvFile1999(data_file)

        recs = list(reader.get_records())

        # nine records in our test file
        assert len(recs) == 9

        for r in recs:
            # each item coming from get_records() is a list containing
            # a single record data item.  The items are setup as lists
            # because they will be fed into the parser as positional *args.
            assert len(r) == 1

            oil_rec, = r

            for row in oil_rec:
                assert len(row) == 22

            assert oil_rec[0]['property_id'] == 'Density_0'
            assert oil_rec[-1]['property_id'] == 'AcuteToxicityofWaterSolubleFractions_454'

    def test_rewind(self):
        reader = EnvCanadaCsvFile1999(data_file)

        recs = list(reader.get_records())

        # nine records in our test file
        assert len(recs) == 9

        recs = list(reader.get_records())

        # After the first iteration, there should be no records left
        assert len(recs) == 0

        reader.rewind()
        recs = list(reader.get_records())

        assert len(recs) == 9


class TestEnvCanadaCsvRecordParser(object):
    reader = EnvCanadaCsvFile1999(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaCsvRecordParser1999()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaCsvRecordParser1999(None, None)

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('ODB00-6', 'API', 26.8),
        ('ODB00-6', 'product_type', 'Crude Oil NOS'),
        ('ODB00-6', 'sample_ids', ['ODB00-6.0', 'ODB00-6.1', 'ODB00-6.2',
                                   'ODB00-6.3']),
        ('ODB00-6', 'fresh_sample_id', 'ODB00-6.0'),
    ])
    def test_init_valid_data_only(self, oil_id, attr, expected):
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if None values are passed in for conditions and
        file_props, we can still construct the parser, but accessing
        certain sample properties could raise an exception.
        """
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        # should construct fine
        parser = EnvCanadaCsvRecordParser1999(*data[0])

        assert getattr(parser, attr) == expected

    @pytest.mark.parametrize('label, expected', [
        ('A Label', 'a_label'),
        ('0.0', '_0_0'),
        ('Density 5 ̊C (g/mL)', 'density_5_c_g_ml'),
        ('14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)',
         '_14ss_h_17ss_h_20_ethylcholestane_c29assss'),
    ])
    def test_slugify(self, label, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == 'ODB00-6']
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('rec, attr, default, expected', [
        ('ODB00-6', 'bogus.bogus', 0, 0),
        ('ODB00-6', 'metadata.API', None, 26.8),
        ('ODB00-6', 'sub_samples.0.bulk_composition.0.measurement.value',
         None, 1.15),
        ('ODB00-6', 'sub_samples.0.bulk_composition.1.measurement.value',
         None, 7),
        ('ODB00-6', 'sub_samples.0.bulk_composition.2.measurement.max_value',
         None, 5),
        ('ODB00-6', 'sub_samples.0.bulk_composition.-1.measurement.max_value',
         None, 0.6),
    ])
    def test_deep_get(self, rec, attr, default, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == rec]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        value = parser.deep_get(parser.oil_obj, attr, default=default)

        assert np.isclose(value, expected)


class TestEnvCanadaCsvRecordMapper(object):
    reader = EnvCanadaCsvFile1999(data_file)

    def deep_get(self, json_obj, attr_path):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        if len(attr_path) > 1:
            return self.deep_get(json_obj[attr_path[0]], attr_path[1:])
        else:
            return json_obj[attr_path[0]]

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaCsvRecordMapper1999()

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            _mapper = EnvCanadaCsvRecordMapper1999(None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('ODB00-6', {'oil_id': 'CCODB00-6',
                     'metadata.name': 'Alaska North Slope (1989)',
                     'metadata.source_id': 'ODB00-6',
                     'metadata.location': 'Alaska, USA',
                     'metadata.reference': {'reference': 'Environmental Emergencies Technology Division, experimental '
                                                         'data, Environment Canada, Ottawa, Ontario, 1983-1989; and '
                                                         'Emergencies Science Division, experimental data, Environment '
                                                         'Canada, Ottawa, Ontario, 1990- 1996. Presently referred to as '
                                                         'the Emergencies Science and Technology Section (ESTS) of '
                                                         'Environment and Climate Change Canada (ECCC)',
                                            'year': 1989},
                     'metadata.product_type': 'Crude Oil NOS',
                     'metadata.API': 26.8,
                     'metadata.comments': None,
                     }),
    ])
    def test_init_valid(self, oil_id, expected):
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if no file props are passed in, we can still
        construct the parser, but accessing reference_date could raise
        a TypeError.
        This is because the reference_date will sometimes need the
        file props if the reference field contains no date information.
        """
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)
        py_json = mapper.py_json()

        for k, v in expected.items():
            if v is not None:
                assert self.deep_get(py_json, k) == v

    def test_save_to_json(self):
        """
        Save an example .json file.  This is not so much a test, but a job
        to provide sample data that people can look at.
        """
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == 'ODB00-5']
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)
        py_json = mapper.py_json()

        py_json['status'] = []

        filename = 'EC-1999-Example-Record.json'
        file_path = os.path.sep.join(
            adios_db.__file__.split(os.path.sep)[:-3] + ['examples', filename]
        )

        print(f'saving to: {file_path}')
        with open(file_path, 'w', encoding="utf-8") as fd:
            json.dump(py_json, fd, indent=4, sort_keys=True)

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('ODB00-6', 0, 'metadata', {'fraction_weathered': {'unit': '%',
                                                           'value': 0},
                                    'name': 'Fresh Oil Sample',
                                    'short_name': 'Fresh Oil',
                                    'sample_id': 'ODB00-6.0'}),
        ('ODB00-6', -1, 'metadata', {'fraction_weathered': {'unit': '%',
                                                            'value': 20},
                                     'name': '20% Evaporated',
                                     'short_name': '20% Evaporated',
                                     'sample_id': 'ODB00-6.3'}),
        ('ODB00-5', 0, 'physical_properties.densities', [
              {'density': {'value': 0.893, 'unit': 'g/mL',
                           'unit_type': 'density'},
               'ref_temp': {'value': 16.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               },
         ]),
        ('ODB00-7', 0, 'physical_properties.dynamic_viscosities', [
              {'ref_temp': {'value': 0.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               'viscosity': {'value': 34, 'unit': 'mPas',
                             'unit_type': 'dynamicviscosity'}},
              {'ref_temp': {'value': 15.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               'viscosity': {'value': 16, 'unit': 'mPas',
                             'unit_type': 'dynamicviscosity'}},
         ]),
        ('ODB00-10', 0, 'physical_properties.kinematic_viscosities', [
              {'ref_temp': {'value': 16.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               'viscosity': {'value': 32, 'unit': 'mm^2/s',
                             'unit_type': 'kinematicviscosity'}},
         ]),
        ('ODB00-66', 0, 'physical_properties.kinematic_viscosities', [
              {'ref_temp': {'value': 38.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               'viscosity': {'value': 1362, 'unit': 'sus',
                             'unit_type': 'kinematicviscosity'}},
         ]),
        ('ODB00-19', 0, 'distillation_data', {
              'type': 'mass fraction',
              'method': '',
              'end_point': {'value': 663.0,
                            'unit': 'C', 'unit_type': 'temperature'},
              'cuts': [
                   {'fraction': {'value': 5.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 66.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 10.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 88.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 15.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 113.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 20.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 137.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 25.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 161.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 30.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 185.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 35.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 211.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 40.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 234.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 45.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 258.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 50.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 283.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 55.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 305.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 60.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 329.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 65.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 356.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 70.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 384.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 75.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 413.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 80.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 444.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 85.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 479.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 90.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 523.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
                   {'fraction': {'value': 95.0, 'unit': '%',
                                 'unit_type': 'massfraction'},
                    'vapor_temp': {'value': 583.0, 'unit': 'C',
                                   'unit_type': 'temperature'}
                    },
              ]
         }),
        ('ODB00-5', 0, 'physical_properties.pour_point', None),
        ('ODB00-6', 0, 'physical_properties.pour_point', {
              'measurement': {'value': -8, 'unit': 'C',
                              'unit_type': 'temperature'}
         }),
        ('ODB00-5', 0, 'physical_properties.flash_point', None),
        ('ODB00-7', 0, 'physical_properties.flash_point', {
              'measurement': {'value': -23, 'unit': 'C',
                              'unit_type': 'temperature'}
         }),
        ('ODB00-6', 0, 'physical_properties.interfacial_tension_air', [
              {'interface': 'air',
               'tension': {'value': 28.1, 'unit': 'mN/m',
                           'unit_type': 'interfacialtension'},
               'ref_temp': {'value': 15.0, 'unit': 'C',
                            'unit_type': 'temperature'}
               },
         ]),
        ('ODB00-6', 0, 'physical_properties.interfacial_tension_water', [
              {'interface': 'water',
               'tension': {'value': 26.1, 'unit': 'mN/m',
                           'unit_type': 'interfacialtension'},
               'ref_temp': {'value': 0.0, 'unit': 'C',
                            'unit_type': 'temperature'}
               },
              {'interface': 'water',
               'tension': {'value': 29.4, 'unit': 'mN/m',
                           'unit_type': 'interfacialtension'},
               'ref_temp': {'value': 15.0, 'unit': 'C',
                            'unit_type': 'temperature'}
               },
         ]),
        ('ODB00-6', 0, 'physical_properties.interfacial_tension_seawater', [
              {'interface': 'seawater',
               'tension': {'value': 23.8, 'unit': 'mN/m',
                           'unit_type': 'interfacialtension'},
               'ref_temp': {'value': 0.0, 'unit': 'C',
                            'unit_type': 'temperature'}
               },
              {'interface': 'seawater',
               'tension': {'value': 27.4, 'unit': 'mN/m',
                           'unit_type': 'interfacialtension'},
               'ref_temp': {'value': 15.0, 'unit': 'C',
                            'unit_type': 'temperature'}
               },
         ]),
        ('ODB00-7', 0, 'environmental_behavior.dispersibilities', [
              {'dispersant': 'Corexit 9500 dispersant',
               'effectiveness': {'value': 46, 'unit': '%',
                                 'unit_type': 'massfraction'}}
         ]),
        ('ODB00-7', 1, 'environmental_behavior.emulsions', [
              {'method': '',
               'ref_temp': {'value': 15.0, 'unit': 'C',
                            'unit_type': 'temperature'},
               'visual_stability': 'Mesostable',
               'complex_modulus': {'value': 120000, 'unit': 'mPa',
                                   'unit_type': 'pressure'},
               'complex_viscosity': {'value': 2600, 'unit': 'mPas',
                                     'unit_type': 'dynamicviscosity'},
               'water_content': {'value': 62, 'unit': '%',
                                 'unit_type': 'massfraction'}},
         ]),
        ('ODB00-7', 0, 'SARA', {
              'method': '',
              'aromatics': {'value': 35, 'unit': '%',
                            'unit_type': 'massfraction'},
              'asphaltenes': {'value': 5, 'unit': '%',
                              'unit_type': 'massfraction'},
              'resins': {'value': 9, 'unit': '%',
                         'unit_type': 'massfraction'},
              'saturates': {'value': 52, 'unit': '%',
                            'unit_type': 'massfraction'}
         }),
    ])
    def test_attribute(self, oil_id, index, attr, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)

        print(f'getting {oil_id}: sub_samples.{index}.{attr}')
        res = mapper.deep_get(mapper.record, f'sub_samples.{index}.{attr}')

        assert res == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('ODB00-6', 0, 'bulk_composition', {
            'list_size': 22,
            'compound_attrs': ('name', 'measurement'),
            'total_groups': None
         }),
        ('ODB00-7', 0, 'compounds', {
            'list_size': 6,
            'compound_attrs': ('name', 'groups', 'measurement'),
            'total_groups': {
                'Volatile Organic Compounds (VOCs)',
            }
         }),
    ])
    def test_compound_list(self, oil_id, index, attr, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)

        compounds = mapper.deep_get(mapper.record,
                                    f'sub_samples.{index}.{attr}')

        # We won't be checking every single compound since there are typically
        # over one hundred to check.  We will verify general properties of our
        # compound list though
        assert type(compounds) == list
        assert len(compounds) == expected['list_size']

        for c in compounds:
            for attr in expected['compound_attrs']:
                assert attr in c

            for attr in ('unit', 'unit_type'):
                assert attr in c['measurement']

            assert ('value' in c['measurement'] or
                    ('min_value' in c['measurement'] and
                     'max_value' in c['measurement']))

        if expected['total_groups'] is not None:
            total_groups = set([sub for c in compounds for sub in c['groups']])
            assert total_groups == expected['total_groups']

    @pytest.mark.parametrize('oil_id, index, attrs', [
        ('ODB00-6', 0, ('densities', 'dynamic_viscosities',
                        'interfacial_tension_air',
                        'interfacial_tension_water',
                        'interfacial_tension_seawater',
                        'pour_point')),
        ('ODB00-7', 0, ('densities', 'dynamic_viscosities',
                        'interfacial_tension_air',
                        'interfacial_tension_water',
                        'interfacial_tension_seawater',
                        'pour_point', 'flash_point')),
    ])
    def test_physical_properties(self, oil_id, index, attrs):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)

        phys = mapper.deep_get(mapper.record,
                               f'sub_samples.{index}.physical_properties')

        assert type(phys) == dict

        # env canada has no kinematic viscosities
        for attr in attrs:
            assert attr in phys

    @pytest.mark.parametrize('oil_id, index, attrs', [
        ('ODB00-6', 0, ('dispersibilities', 'emulsions')),
        ('ODB00-7', 0, ('adhesion', 'dispersibilities', 'emulsions',
                        'ests_evaporation_test')),
    ])
    def test_environmental_behavior(self, oil_id, index, attrs):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['oil_index']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser1999(*data[0])
        mapper = EnvCanadaCsvRecordMapper1999(parser)

        env = mapper.deep_get(mapper.record,
                              f'sub_samples.{index}.environmental_behavior')

        assert type(env) == dict

        for attr in attrs:
            assert attr in env
