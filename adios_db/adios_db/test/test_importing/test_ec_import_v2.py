"""
tests of the Environment Canada data import modules

As complete as possible, because we want to test for correctness,
and we also want to document how it works.
Either we test it correctly, or we test it in an episodic manner on the
real dataset.
"""
import os
from pathlib import Path
import json

import numpy as np
import pytest

dateutil = pytest.importorskip("dateutil")

import adios_db
try: # can't work if dateutil isn't there
    from adios_db.data_sources.env_canada.v2 import (EnvCanadaCsvFile,
                                                     EnvCanadaCsvRecordParser,
                                                     EnvCanadaCsvRecordMapper,
                                                     InvalidFileError)
except:
    pass

from pprint import pprint

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing


example_dir = Path(__file__).resolve().parent / 'example_data'
example_index = example_dir / 'index.txt'
data_file = example_dir / 'EnvCanadaCsvTestSet.csv'


class TestEnvCanadaCsvFile(object):
    def test_init(self):
        with pytest.raises(TypeError):
            _reader = EnvCanadaCsvFile()

    def test_init_nonexistant_file(self):
        with pytest.raises(FileNotFoundError):
            _reader = EnvCanadaCsvFile('bogus.file')

    def test_init_invalid_file(self):
        with pytest.raises(InvalidFileError):
            _reader = EnvCanadaCsvFile(example_index)

    def test_init_with_valid_file(self):
        reader = EnvCanadaCsvFile(data_file)

        assert reader.name == data_file

    def test_get_records(self):
        reader = EnvCanadaCsvFile(data_file)
        recs = list(reader.get_records())

        # five records in our test file
        assert len(recs) == 5

        for r in recs:
            # each item coming from get_records() is a list containing
            # a single record data item.  The items are setup as lists
            # because they will be fed into the parser as positional *args.
            assert len(r) == 1

            oil_rec, = r

            for row in oil_rec:
                assert len(row) == 23

            assert oil_rec[0]['property_id'] == 'Density_0'
            assert oil_rec[-1]['property_id'] == 'Biomarkers_292'

    def test_rewind(self):
        reader = EnvCanadaCsvFile(data_file)
        recs = list(reader.get_records())

        # five records in our test file
        assert len(recs) == 5

        recs = list(reader.get_records())

        # After the first iteration, there should be no records left
        assert len(recs) == 0

        reader.rewind()
        recs = list(reader.get_records())

        assert len(recs) == 5


class TestEnvCanadaCsvRecordParser(object):
    reader = EnvCanadaCsvFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaCsvRecordParser()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaCsvRecordParser(None, None)

    @pytest.mark.parametrize('oil_id, attr, expected', [
        ('2713', 'API', 31.3),
        ('2713', 'product_type', 'Crude Oil NOS'),
        ('2713', 'sample_ids', [2713.1, '2713.2.3', '2713.2.2', '2713.2.1']),
        ('2713', 'fresh_sample_id', 2713.1),
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
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        # should construct fine
        parser = EnvCanadaCsvRecordParser(*data[0])

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
                if str(r[0][0]['ests']) == '2234']
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('rec, attr, default, expected', [
        ('2234', 'metadata.API', None, 20.9),
        ('2234', 'sub_samples.0.compounds.-1.measurement.value', None, 240),
        ('2234', 'sub_samples.4.compounds.-1.measurement.value', None, 305),
        ('2234', 'bogus.bogus', 0, 0),
    ])
    def test_deep_get(self, rec, attr, default, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == rec]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])

        assert np.isclose(parser.deep_get(parser.oil_obj, attr,
                                          default=default),
                          expected)


class TestEnvCanadaCsvRecordMapper(object):
    reader = EnvCanadaCsvFile(data_file)

    def deep_get(self, json_obj, attr_path):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        if len(attr_path) > 1:
            return self.deep_get(json_obj[attr_path[0]], attr_path[1:])
        else:
            return json_obj[attr_path[0]]

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaCsvRecordMapper()

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            _mapper = EnvCanadaCsvRecordMapper(None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', {'oil_id': 'EC02713',
                  'metadata.name': 'Alaska North Slope [2015]',
                  'metadata.source_id': '2713',
                  'metadata.location': 'Alaska, USA',
                  'metadata.reference': {
                      'reference': "Environment and Climate Change Canada, "
                                   "Environment Canada Crude Oil and "
                                   "Petroleum Product Database, "
                                   "Environment and Climate Change Canada, "
                                   "2021.\n\n"
                                   "url: https://open.canada.ca/data/en/dataset/53c38f91-35c8-49a6-a437-b311703db8c5",
                      'year': 2021
                  },
                  'metadata.sample_date': '2015-03-22',
                  'metadata.product_type': 'Crude Oil NOS',
                  'metadata.API': 31.3,
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
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)
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
                if str(r[0][0]['ests']) == '2234']
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)
        py_json = mapper.py_json()

        py_json['status'] = []

        filename = 'EC-Example-Record.json'
        file_path = os.path.sep.join(
            adios_db.__file__.split(os.path.sep)[:-3] + ['examples', filename]
        )

        print(f'saving to: {file_path}')
        with open(file_path, 'w', encoding="utf-8") as fd:
            json.dump(py_json, fd, indent=4, sort_keys=True)

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2713', 0, 'metadata', {'fraction_weathered': {'unit': '%',
                                                        'value': 0.0},
                                 'name': 'Fresh Oil Sample',
                                 'short_name': 'Fresh Oil',
                                 'sample_id': '2713.1'}),
        ('2713', -1, 'metadata', {'fraction_weathered': {'unit': '%',
                                                         'value': 36.8},
                                  'name': '36.8% Evaporated',
                                  'short_name': '36.8% Evaporated',
                                  'sample_id': '2713.2.1'}),
        ('2713', 0, 'physical_properties.densities', [
            {'density': {'value': 0.8639, 'unit': 'g/mL',
                         'unit_type': 'density',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'method': 'ASTM D5002'},
            {'density': {'value': 0.8751, 'unit': 'g/mL',
                         'unit_type': 'density',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'method': 'ASTM D5002'},
         ]),
        ('2713', 0, 'physical_properties.dynamic_viscosities', [
            {'method': 'ASTM D7042',
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'viscosity': {'value': 10, 'unit': 'mPa.s',
                           'unit_type': 'dynamicviscosity',
                           'standard_deviation': 0, 'replicates': 3}},
            {'method': 'ASTM D7042',
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'viscosity': {'value': 17.9, 'unit': 'mPa.s',
                           'unit_type': 'dynamicviscosity',
                           'standard_deviation': 0.001, 'replicates': 3}},
         ]),
        ('2234', 3, 'physical_properties.dynamic_viscosities', [
            {'method': 'ESTS 12.06/x.x/M',
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'shear_rate': {'value': 10.0, 'unit': '1/s',
                            'unit_type': 'angularvelocity'},
             'viscosity': {'value': 1000000.0, 'unit': 'mPa.s',
                           'unit_type': 'dynamicviscosity',
                           'standard_deviation': 67000.0, 'replicates': 3}},
            {'method': 'ESTS 12.06/x.x/M',
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'shear_rate': {'value': 0.1, 'unit': '1/s',
                            'unit_type': 'angularvelocity'},
             'viscosity': {'value': 90000000.0, 'unit': 'mPa.s',
                           'unit_type': 'dynamicviscosity',
                           'standard_deviation': 2233480, 'replicates': 3}},
         ]),
        ('2713', 0, 'distillation_data', {
            'type': 'mass fraction',
            'method': 'Merged ASTM D7169 & ASTM D6730 mod.',
            'end_point': {'min_value': 720.0, 'max_value': None,
                          'unit': 'C', 'unit_type': 'temperature'},
            'cuts': [
                {'fraction': {'value': 0.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': -12, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 5.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 60, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 10.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 92, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 15.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 119, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 20.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 148, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 25.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 181, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 30.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 216, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 35.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 248, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 40.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 278, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 45.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 308, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 50.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 339, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 55.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 371, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 60.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 404, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 65.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 436, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 70.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 473, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 75.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 516, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 80.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 568, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 85.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 623, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
                {'fraction': {'value': 90.0, 'unit': '%',
                              'unit_type': 'massfraction'},
                 'vapor_temp': {'value': 680, 'unit': 'C',
                                'unit_type': 'temperature'}
                 },
            ]
         }),
        ('561', 0, 'physical_properties.pour_point', None),
        ('2713', 0, 'physical_properties.pour_point', {
            'method': 'ASTM D97',
            'measurement': {'value': -51, 'unit': 'C',
                            'unit_type': 'temperature',
                            'standard_deviation': 2,
                            'replicates': 3}}
         ),
        ('2713', 0, 'physical_properties.flash_point', None),
        ('2713', 1, 'physical_properties.flash_point', {
            'method': 'ASTM D7094',
            'measurement': {'value': 23, 'unit': 'C',
                            'unit_type': 'temperature',
                            'standard_deviation': 1.2,
                            'replicates': 3}}
         ),
        ('2713', 0, 'physical_properties.interfacial_tension_air', [
            {'interface': 'air',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 27.1, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.2, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
            {'interface': 'air',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 27.7, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.8, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
         ]),
        ('2713', 0, 'physical_properties.interfacial_tension_water', [
            {'interface': 'water',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 21.3, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.3, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
            {'interface': 'water',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 24.1, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.2, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
         ]),
        ('2713', 0, 'physical_properties.interfacial_tension_seawater', [
            {'interface': 'seawater',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 19.8, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.4, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
            {'interface': 'seawater',
             'method': 'ESTS 12.12/x.x/M',
             'tension': {'value': 22.8, 'unit': 'mN/m',
                         'unit_type': 'interfacialtension',
                         'standard_deviation': 0.2, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C',
                          'unit_type': 'temperature'}
             },
         ]),
        ('2713', 0, 'environmental_behavior.dispersibilities', [
            {'dispersant': 'Corexit 9500 Dispersant',
             'method': 'ASTM F2059',
             'effectiveness': {'value': 46, 'unit': '%',
                               'unit_type': 'massfraction',
                               'standard_deviation': 4,
                               'replicates': 6}}
         ]),
        ('2234', 0, 'environmental_behavior.emulsions', [
            {'age': {'value': 0, 'unit': 'day', 'unit_type': 'time'},
             'method': 'ESTS 13.02/x.x/M',
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'visual_stability': 'Entrained',
             'complex_modulus': {'value': 45, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 7, 'replicates': 6},
             'complex_viscosity': {'value': 7, 'unit': 'Pa.s',
                                   'unit_type': 'dynamicviscosity',
                                   'standard_deviation': 1, 'replicates': 6},
             'loss_modulus': {'value': 42, 'unit': 'Pa',
                              'unit_type': 'pressure',
                              'standard_deviation': 6, 'replicates': 6},
             'storage_modulus': {'value': 14, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 3, 'replicates': 6},
             'tan_delta_v_e': {'value': 3, 'unit': None,
                               'unit_type': 'unitless',
                               'standard_deviation': 0.4, 'replicates': 6},
             'water_content': {'value': 40, 'unit': '%',
                               'unit_type': 'massfraction',
                               'standard_deviation': 2, 'replicates': 9}},
            {'age': {'value': 7, 'unit': 'day', 'unit_type': 'time'},
             'method': 'ESTS 13.02/x.x/M',
             'ref_temp': {'value': 15.0, 'unit': 'C',
                          'unit_type': 'temperature'},
             'complex_modulus': {'value': 31, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 7, 'replicates': 6},
             'complex_viscosity': {'value': 5, 'unit': 'Pa.s',
                                   'unit_type': 'dynamicviscosity',
                                   'standard_deviation': 1, 'replicates': 6},
             'loss_modulus': {'value': 31, 'unit': 'Pa',
                              'unit_type': 'pressure',
                              'standard_deviation': 7, 'replicates': 6},
             'storage_modulus': {'value': 2, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 1, 'replicates': 6},
             'tan_delta_v_e': {'value': 12, 'unit': None,
                               'unit_type': 'unitless',
                               'standard_deviation': 2, 'replicates': 5},
             'water_content': {'value': 16, 'unit': '%',
                               'unit_type': 'massfraction',
                               'standard_deviation': 2, 'replicates': 9}}
         ]),
        ('2713', 0, 'SARA', {
            'method': 'ESTS 12.11/3.0/M',
            'aromatics': {'value': 32, 'unit': '%',
                          'unit_type': 'massfraction'},
            'asphaltenes': {'value': 4, 'unit': '%',
                            'unit_type': 'massfraction',
                            'standard_deviation': 0.1,
                            'replicates': 3},
            'resins': {'value': 6, 'unit': '%',
                       'unit_type': 'massfraction',
                       'standard_deviation': 0.2,
                       'replicates': 3},
            'saturates': {'value': 58, 'unit': '%',
                          'unit_type': 'massfraction'}
         }),
    ])
    def test_attribute(self, oil_id, index, attr, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

        res = mapper.deep_get(mapper.record, f'sub_samples.{index}.{attr}')

        assert res == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2234', 0, 'compounds', {
            'list_size': 91,
            'compound_attrs': ('name', 'method', 'groups', 'measurement'),
            'total_groups': {
                'Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)',
                'Biomarkers',
                'Other Priority PAHs',
                'n-Alkanes',
            }
         }),
        ('561', 0, 'compounds', {
            'list_size': 114,
            'compound_attrs': ('name', 'method', 'groups', 'measurement'),
            'total_groups': {
                'Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)',
                'C3-C6 Alkyl Benzenes',
                'Biomarkers',
                'BTEX group',
                'Other Priority PAHs',
                'n-Alkanes',
            }
         }),
        ('2234', 0, 'bulk_composition', {
            'list_size': 9,
            'compound_attrs': ('name', 'method', 'measurement'),
            'total_groups': None
         }),
    ])
    def test_compound_list(self, oil_id, index, attr, expected):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

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

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('2234', 0, {
            'fractions': (16.0, 50.0, 193.0, 40.0),
         }),
        ('561', 0, {
            'fractions': (68.0, 171.0, 302.0, 60.0),
         }),
    ])
    def test_ccme(self, oil_id, index, expected):
        """
        CCME object is a struct.
        """
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

        ccme = mapper.deep_get(mapper.record,
                               f'sub_samples.{index}.CCME')

        assert type(ccme) == dict

        for attr, fraction in zip(('F1', 'F2', 'F3', 'F4'),
                                  expected['fractions']):
            assert attr in ccme

            for measurement_attr in ('value', 'unit', 'unit_type'):
                assert measurement_attr in ccme[attr]

            assert ccme[attr]['value'] == fraction

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('2234', 0, {
            'list_sizes': [8, 8, 9],
         }),
    ])
    def test_ests_fractions(self, oil_id, index, expected):
        """
        ESTS_hydrocarbon_fractions object is a struct consisting of
        attributes that are compound lists.
        """
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

        ests_fractions = mapper.deep_get(mapper.record,
                                         f'sub_samples.{index}'
                                         '.ESTS_hydrocarbon_fractions')

        assert type(ests_fractions) == dict

        assert expected['list_sizes'] == [len(ests_fractions[attr]) for attr in
                                          ('saturates',
                                           'aromatics',
                                           'GC_TPH')]

    @pytest.mark.parametrize('oil_id, index, attrs', [
        ('2234', 0, ('pour_point', 'flash_point',
                     'densities', 'dynamic_viscosities',
                     'interfacial_tension_air',
                     'interfacial_tension_water',
                     'interfacial_tension_seawater')),
        ('561', 0, ('densities', 'dynamic_viscosities',
                    'interfacial_tension_air',
                    'interfacial_tension_water',
                    'interfacial_tension_seawater')),
    ])
    def test_physical_properties(self, oil_id, index, attrs):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

        phys = mapper.deep_get(mapper.record,
                               f'sub_samples.{index}.physical_properties')

        assert type(phys) == dict

        # env canada has no kinematic viscosities
        for attr in attrs:
            assert attr in phys

    @pytest.mark.parametrize('oil_id, index, attrs', [
        ('2234', 0, ('dispersibilities', 'emulsions',
                     'ests_evaporation_test')),
        ('506', 0, ('adhesion', 'dispersibilities', 'emulsions',
                    'ests_evaporation_test')),
        ('561', 0, ('adhesion',)),
    ])
    def test_environmental_behavior(self, oil_id, index, attrs):
        self.reader.rewind()
        data = [r for r in self.reader.get_records()
                if str(r[0][0]['ests']) == oil_id]
        assert len(data) == 1

        parser = EnvCanadaCsvRecordParser(*data[0])
        mapper = EnvCanadaCsvRecordMapper(parser)

        env = mapper.deep_get(mapper.record,
                              f'sub_samples.{index}.environmental_behavior')

        pprint(env)

        assert type(env) == dict

        # env canada has no kinematic viscosities
        for attr in attrs:
            assert attr in env
