"""
tests of the Environment Canada data import modules

As complete as possible, because we want to test for correctness,
and we also want to document how it works.
Either we test it correctly, or we test it in an episodic manner on the
real dataset.
"""
import os
from numbers import Number
from pathlib import Path
import json

import pytest
import numpy as np

try:
    from slugify import Slugify
    from openpyxl.utils.exceptions import InvalidFileException
    HAVE_OPTIONAL = True
except ImportError:
    HAVE_OPTIONAL = False
    pytest.skip("You need the awesome-slugify and openpyxl packages "
                "to run these tests", allow_module_level=True)

import adios_db
from adios_db.data_sources.env_canada.v1 import (EnvCanadaOilExcelFile,
                                                 EnvCanadaRecordParser,
                                                 EnvCanadaRecordMapper,
                                                 EnvCanadaSampleMapper)

# Pass the --import command line option if you want these to run.
pytestmark = pytest.mark.importing


example_dir = Path(__file__).resolve().parent / 'example_data'
example_index = example_dir / 'index.txt'
data_file = example_dir / 'EnvCanadaTestSetNew.xlsm'


class TestEnvCanadaOilExcelFile(object):
    def test_init(self):
        with pytest.raises(TypeError):
            _reader = EnvCanadaOilExcelFile()

    def test_init_nonexistant_file(self):
        with pytest.raises(InvalidFileException):
            _reader = EnvCanadaOilExcelFile('bogus.file')

    def test_init_invalid_file(self):
        with pytest.raises(InvalidFileException):
            _reader = EnvCanadaOilExcelFile(example_index)

    def test_init_with_valid_file(self):
        reader = EnvCanadaOilExcelFile(data_file)

        assert reader.name == data_file

        # just test that the file props reference the correct document info
        assert reader.file_props['name'] == 'EnvCanadaTestSetNew.xlsm'
        assert reader.file_props['creator'] is None

        # We should have five oil records
        assert reader.col_indexes == {'2234': [5, 6, 7, 8, 9],
                                      '506': [10, 11, 12, 13],
                                      '2713': [14, 15, 16, 17],
                                      '540': [18, 19],
                                      '561': [20, 21, 22, 23],
                                      }

        # There are literally hundreds of fields here, so let's just check
        # some of the individual category/field combinations
        assert reader.field_indexes[None]['Oil'] == [0]
        assert reader.field_indexes[None]['Weathered %:'] == [5]

        # the last row in our spreadsheet
        assert (reader.field_indexes
                ['Biomarkers']
                ['14ß(H),17ß(H)-20-Ethylcholestane (C29αßß)']) == [446]

    def test_get_record(self):
        print('opening reader...')
        reader = EnvCanadaOilExcelFile(data_file)

        print('get rec = 2234...')
        rec, conditions, file_props = reader.get_record('2234')

        # There are literally hundreds of fields here, so let's just check
        # some of the individual category/field combinations
        assert rec[None]['Oil'] == ['Access West Blend Winter',
                                    None, None, None, None]
        assert rec[None]['Weathered %:'] == [0, 0.0853, 0.1686, 0.2534, 0.2645]

        # the last row in our spreadsheet
        assert np.allclose(rec
                           ['Biomarkers']
                           ['14ß(H),17ß(H)-20-Ethylcholestane (C29αßß)'],
                           [240.15,
                            254.44,
                            278.78,
                            291.54,
                            304.77])

        # now the content of our conditions
        assert conditions[None]['Oil'] == {
            'unit': 'Unit of measurment',
            'ref_temp': 'Temperature',
            'condition': 'Condition of analysis',
        }
        assert (conditions
                ['Biomarkers']
                ['14ß(H),17ß(H)-20-Ethylcholestane (C29αßß)'] == {
                    'unit': 'µg/g',
                    'ref_temp': None,
                    'condition': None,
                 })

        # Now the content of the returned file props
        assert file_props['name'] == 'EnvCanadaTestSetNew.xlsm'
        assert file_props['creator'] is None

    def test_get_records(self):
        reader = EnvCanadaOilExcelFile(data_file)

        recs = list(reader.get_records())

        # five records in our test file
        assert len(recs) == 5

        for r in recs:
            # each item coming from records() is a record set containing
            # record data and file props
            assert len(r) == 3


class TestEnvCanadaRecordParser(object):
    reader = EnvCanadaOilExcelFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaRecordParser()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaRecordParser(None, None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', 2020),
    ])
    def test_init_valid_data_only(self, oil_id, expected):
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if None values are passed in for conditions and
        file_props, we can still construct the parser, but accessing
        certain sample properties could raise an exception.
        """
        data, _conditions, _file_props = self.reader.get_record(oil_id)

        # should construct fine
        parser = EnvCanadaRecordParser(data, None, None)

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', 2020),
        ('2234', 2020),
    ])
    def test_init_valid_data_and_file_props(self, oil_id, expected):
        """
        The reference_date will sometimes need the file props if the
        reference field contains no date information.  check that the
        file props are correctly parsed.
        """
        data, _conditions, file_props = self.reader.get_record(oil_id)
        parser = EnvCanadaRecordParser(data, None, file_props)

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('label, expected', [
        ('A Label', 'a_label'),
        ('0.0', '_0_0'),
        ('Density 5 ̊C (g/mL)', 'density_5_c_g_ml'),
        ('14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)',
         '_14ss_h_17ss_h_20_ethylcholestane_c29assss'),
    ])
    def test_slugify(self, label, expected):
        data, conditions, file_props = self.reader.get_record('2234')
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('path, expected', [
        ('gc_tah',
         'GC-TAH'),
        ('gc_tah.tah',
         'Gas Chromatography-Total aromatic hydrocarbon (GC-TAH)'),
        (['gc_tah', 'tah'],
         'Gas Chromatography-Total aromatic hydrocarbon (GC-TAH)'),
        pytest.param('bogus', 'does not matter',
                     marks=pytest.mark.raises(exception=KeyError)),
        pytest.param('gc_total_aromatic_hydrocarbon.bogus', 'does not matter',
                     marks=pytest.mark.raises(exception=KeyError)),
    ])
    def test_get_label(self, path, expected):
        data, conditions, file_props = self.reader.get_record('2234')
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        assert parser.get_label(path) == expected

    @pytest.mark.parametrize('rec, attr, expected', [
        ('2234', 'name', 'Access West Blend Winter'),
        ('2234', 'oil_id', 'EC02234'),
        ('2234', 'ests_codes', ['2234.1.1 A', '2234.1.4.1 ', '2234.1.3.1 ',
                                '2234.1.2.1 ', '2234.1.5.1 ']),
        ('2234', 'weathering', [0.0, 0.0853, 0.1686, 0.2534, 0.2645]),
        ('2713', 'reference', {'reference': 'Personal communication from '
                                            'Fatemeh Mirnaghi (ESTS), '
                                            'date: April 21, 2020.',
                               'year': 2020}),
        ('2234', 'sample_date', '2013-04-08'),
        ('2234', 'comments', 'Via CanmetEnergy, Natural Resources Canada'),
        ('2234', 'location', 'Alberta, Canada'),
        ('2234', 'product_type', 'Crude Oil NOS'),
        ('540', 'product_type', 'Refined Product NOS'),
    ])
    def test_attrs(self, rec, attr, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        assert getattr(parser, attr) == expected

    @pytest.mark.parametrize('rec, attr, index, expected', [
        ('2234', 'api_gravity.gravity', 0, 20.927),
        ('2234', 'api_gravity.gravity', 4, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, 240.15),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, 304.77),
    ])
    def test_vertical_slice(self, rec, attr, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        subsample = parser.vertical_slice(index)

        l1, l2 = attr.split('.')  # two dotted levels
        assert np.isclose(subsample[l1][l2], expected)

    @pytest.mark.parametrize('rec, attr, index, default, expected', [
        ('2234', 'api_gravity.gravity', 0, None, 20.927),
        ('2234', 'api_gravity.gravity', 4, None, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, None,
         240.15),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, None,
         304.77),
        ('2234', 'bogus.bogus', 0, 0, 0),
    ])
    def test_samples(self, rec, attr, index, default, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].deep_get(attr, default=default),
                           expected)


class TestEnvCanadaSampleParser(object):
    reader = EnvCanadaOilExcelFile(data_file)

    @pytest.mark.parametrize('rec, attr, index, default, expected', [
        ('2234', 'api_gravity.gravity', 0, None, 20.927),
        ('2234', 'api_gravity.gravity', 4, None, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, None,
         240.15),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, None,
         304.77),
        ('2234', 'bogus.bogus', 0, 0, 0),
    ])
    def test_deep_get(self, rec, attr, index, default, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].deep_get(attr, default=default),
                           expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, 20.927),
        ('2234', 4, 8.01),
    ])
    def test_api(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].api, expected)

    def compare_expected(self, value, expected):
        """
        compare a value to an expected value
        """
        if not type(value) == type(expected):
            return False

        if isinstance(value, list):
            return all([self.compare_expected(*args)
                        for args in zip(value, expected)])
        elif isinstance(value, dict):
            ret = []

            for k, v in value.items():
                ret.append(self.compare_expected(v, expected[k]))

            return all(ret)
        elif isinstance(value, Number):
            return np.isclose(value, expected)
        else:
            return value == expected

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'density': [0.92526, None, 0.93988],
                     'method': ['ASTM D5002', None, 'ASTM D5002'],
                     'ref_temp': [
                         {'unit': 'C', 'value': 15.0},
                         {'unit': 'C', 'value': 5.0},
                         {'unit': 'C', 'value': 0.0},
                     ],
                     'replicates': [3, None, 3],
                     'standard_deviation': [0.00050914, None, 0.0003377],
                     'unit': ['g/mL', 'g/mL', 'g/mL']}),
        ('2234', 4, {'density': [1.014, None, 1.0211],
                     'method': ['ASTM D5002', None, 'ASTM D5002'],
                     'ref_temp': [
                         {'unit': 'C', 'value': 15.0},
                         {'unit': 'C', 'value': 5.0},
                         {'unit': 'C', 'value': 0.0},
                     ],
                     'replicates': [3, None, 3],
                     'standard_deviation': [1.5275e-06, None, 4.5092e-06],
                     'unit': ['g/mL', 'g/mL', 'g/mL']}),
    ])
    def test_densities(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].densities, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {
            'condition': [
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate=1 1/s',
                '(Non-Newtonian) Shear rate=0.1 1/s',
                'Unkown behavoir',
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate= 1 1/s',
                '(Non-Newtonian) Shear rate=0.01 1/s',
                'Unkown behavoir',
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate= 1 1/s',
                '(Non-Newtonian) Shear rate=0.01 1/s',
                'Unkown behavoir'
            ],
            'method': [
                '12.06/x.x/M', None, None, None, None, None,
                None, None, None, None, None, None,
                '12.06/x.x/M', None, None, None, None, None
            ],
            'ref_temp': [
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
            ],
            'replicates': [
                3, None, None, None, None, None,
                None, None, None, None, None, None,
                3, None, None, None, None, None
            ],
            'standard_deviation': [
                8.271, None, None, None, None, None,
                None, None, None, None, None, None,
                24.44, None, None, None, None, None
            ],
            'unit': [
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s',
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s',
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s'
            ],
            'viscosity': [
                350, None, None, None, None, None,
                None, None, None, None, None, None,
                1300, None, None, None, None, None
            ]
         }),
        ('2234', 4, {
            'condition': [
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate=1 1/s',
                '(Non-Newtonian) Shear rate=0.1 1/s',
                'Unkown behavoir',
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate= 1 1/s',
                '(Non-Newtonian) Shear rate=0.01 1/s',
                'Unkown behavoir',
                'Newtonian behavoir (Shear rate independent)',
                '(Non-Newtonian) Shear rate=100 1/s',
                '(Non-Newtonian) Shear rate=10 1/s',
                '(Non-Newtonian) Shear rate= 1 1/s',
                '(Non-Newtonian) Shear rate=0.01 1/s',
                'Unkown behavoir'
            ],
            'method': [
                None, None, None, '12.06/x.x/M', None, None,
                None, None, None, None, None, None,
                None, None, None, None, None, None
            ],
            'ref_temp': [
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
            ],
            'replicates': [
                None, None, None, 3, None, None,
                None, None, None, None, None, None,
                None, None, None, None, None, None
            ],
            'standard_deviation': [
                None, None, None, 119300.0, None, None,
                None, None, None, None, None, None,
                None, None, None, None, None, None
            ],
            'unit': [
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s',
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s',
                'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s', 'mPa.s'
            ],
            'viscosity': [
                None, None, None, 7909000, None, None,
                None, None, None, None, None, None,
                None, None, None, None, None, None
            ]
        }),
    ])
    def test_dvis(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].dvis, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {
            'interface': [
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface',
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface',
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface'
            ],
            'interfacial_tension': [
                30.197, 24.237, 23.827,
                None, None, None,
                31.147, 24.78, 24.96
            ],
            'method': [
                '12.12/x.x/M', '12.12/x.x/M', '12.12/x.x/M',
                None, None, None,
                '12.12/x.x/M', '12.12/x.x/M', '12.12/x.x/M'
            ],
            'ref_temp': [
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
            ],
            'replicates': [3, 3, 3, None, None, None, 3, 3, 3],
            'standard_deviation': [
                0.11372, 0.045092, 0.020817,
                None, None, None,
                0.15044, 0.13454, 0.24637
            ],
            'unit': [
                'mN/m', 'mN/m', 'mN/m',
                'mN/m', 'mN/m', 'mN/m',
                'mN/m', 'mN/m', 'mN/m'
            ]
         }),
        ('2234', 4, {
            'interface': [
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface',
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface',
                'Oil/ air interface',
                'Oil/water interface',
                'Oil/salt water, 3.3% NaCl interface'
            ],
            'interfacial_tension': [
                'Too Viscous', 'Too Viscous', 'Too Viscous',
                None, None, None,
                'Too Viscous', 'Too Viscous', 'Too Viscous'
            ],
            'method': [
                '12.12/x.x/M', '12.12/x.x/M', '12.12/x.x/M',
                None, None, None,
                '12.12/x.x/M', '12.12/x.x/M', '12.12/x.x/M'
            ],
            'ref_temp': [
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 15.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 5.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0},
                {'unit': 'C', 'value': 0.0}
            ],
            'replicates': [3, 3, 3, None, None, None, 3, 3, 3],
            'standard_deviation': [
                'Too Viscous', None, None,
                None, None, None,
                None, None, None
            ],
            'unit': [
                'mN/m', 'mN/m', 'mN/m',
                'mN/m', 'mN/m', 'mN/m',
                'mN/m', 'mN/m', 'mN/m'
            ]
         }),
    ])
    def test_ifts(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ifts, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'flash_point': '< -5',
                     'method': 'ASTM D7094',
                     'replicates': None,
                     'standard_deviation': None}),
        ('2234', 4, {'flash_point': 173,
                     'method': 'ASTM D7094',
                     'replicates': None,
                     'standard_deviation': None}),
    ])
    def test_flash_point(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].flash_point, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'method': 'ASTM D97',
                     'pour_point': '< -25',
                     'replicates': None,
                     'standard_deviation': None}),
        ('2234', 4, {'method': 'ASTM D97',
                     'pour_point': 33,
                     'replicates': None,
                     'standard_deviation': None}),
    ])
    def test_pour_point(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].pour_point, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'_0_05': 35,
                     '_0_1': 52,
                     '_0_15': 70,
                     '_0_2': 88,
                     '_0_25': 106,
                     '_0_3': 138,
                     '_0_35': 207,
                     '_0_4': 260,
                     '_0_45': 294,
                     '_0_5': 319,
                     '_0_55': 343,
                     '_0_6': 365,
                     '_0_65': 385,
                     '_0_7': 405,
                     '_0_75': 424,
                     '_0_8': 442,
                     '_0_85': 459,
                     '_0_9': 478,
                     '_0_95': 499,
                     '_1': None,
                     'fbp': 522,
                     'initial_boiling_point': None,
                     'method': 'ASTM D7169'}),
        ('2234', 4, {'_0_05': 294,
                     '_0_1': 312,
                     '_0_15': 328,
                     '_0_2': 342,
                     '_0_25': 355,
                     '_0_3': 368,
                     '_0_35': 380,
                     '_0_4': 392,
                     '_0_45': 403,
                     '_0_5': 415,
                     '_0_55': 426,
                     '_0_6': 435,
                     '_0_65': 445,
                     '_0_7': 454,
                     '_0_75': 464,
                     '_0_8': 475,
                     '_0_85': 485,
                     '_0_9': 495,
                     '_0_95': 503,
                     '_1': None,
                     'fbp': 511,
                     'initial_boiling_point': None,
                     'method': 'ASTM D7169'}),
    ])
    def test_boiling_point_distribution(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].boiling_point_distribution,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('506', 0, {'_100': 7.14,
                    '_120': 9.04,
                    '_140': 11.24,
                    '_160': 13.84,
                    '_180': 16.54,
                    '_200': 18.94,
                    '_250': 25.64,
                    '_300': 33.14,
                    '_350': 41.14,
                    '_40': 2.32,
                    '_400': 48.94,
                    '_450': 57.24,
                    '_500': 64.34,
                    '_550': 70.44,
                    '_60': 2.97,
                    '_600': 75.54,
                    '_650': 80.04,
                    '_700': None,
                    '_80': 5.44,
                    'method': '5.10/x.x/M',
                    'temperature_c': None}),
        ('506', 3, {'_100': 0,
                    '_120': 0,
                    '_140': 0,
                    '_160': 0,
                    '_180': 0.1,
                    '_200': 0.7,
                    '_250': 6.8,
                    '_300': 16.4,
                    '_350': 26.9,
                    '_40': 0,
                    '_400': 37.3,
                    '_450': 48.4,
                    '_500': 58.2,
                    '_550': 66.5,
                    '_60': 0,
                    '_600': 73.4,
                    '_650': 79.3,
                    '_700': None,
                    '_80': 0,
                    'method': '5.10/x.x/M',
                    'temperature_c': None}),
    ])
    def test_boiling_point_cumulative_fraction(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index]
                                     .boiling_point_cumulative_fraction,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'value': 18.03, 'unit': 'g/cm^2',
                     'unit_type': 'needleadhesion',
                     'method': 'ESTS: 12.12/x.x/M',
                     'replicates': 3,
                     'standard_deviation': 1.05}),
        ('2713', 3, {'value': 56.39, 'unit': 'g/cm^2',
                     'unit_type': 'needleadhesion',
                     'method': 'ESTS: 12.12/x.x/M',
                     'replicates': 3,
                     'standard_deviation': 3.09}),
    ])
    def test_adhesion(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].adhesion, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'a_for_ev_a_b_ln_t_c': None,
                     'a_for_ev_a_b_ln_t': 1.72,
                     'a_for_ev_a_b_sqrt_t': None,
                     'b_for_ev_a_b_ln_t_c': None,
                     'b_for_ev_a_b_ln_t': 0.045,
                     'b_for_ev_a_b_sqrt_t': None,
                     'c_for_ev_a_b_ln_t_c': None,
                     'method': 'ESTS: 13.01/x.x/M'}),
        ('2234', 4, {'a_for_ev_a_b_ln_t_c': None,
                     'a_for_ev_a_b_ln_t': None,
                     'a_for_ev_a_b_sqrt_t': None,
                     'b_for_ev_a_b_ln_t_c': None,
                     'b_for_ev_a_b_ln_t': None,
                     'b_for_ev_a_b_sqrt_t': None,
                     'c_for_ev_a_b_ln_t_c': None,
                     'method': None}),
    ])
    def test_evaporation_eqs(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ests_evaporation_test,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {
            'conditions': {
                'emulsion_complex_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_complex_viscosity': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa.s', 'unit_type': 'dynamicviscosity',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa.s', 'unit_type': 'dynamicviscosity',
                     'converted': True}
                ],
                'emulsion_loss_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_storage_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': 'Pa', 'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_tan_delta_v_e': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}],
                'emulsion_visual_stability': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}],
                'emulsion_water_content': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0},
                     'unit': '%', 'unit_type': 'massfraction',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp':  {'unit': 'C', 'value': 15.0},
                     'unit': '%', 'unit_type': 'massfraction',
                     'converted': True}],
                'method': [
                    {'condition': 'On the day of formation',
                     'ref_temp': None, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': None, 'unit': None,
                     'converted': True}],
                'replicates': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}],
                'standard_deviation': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}]},
            'emulsion_complex_modulus': [45, 31],
            'emulsion_complex_viscosity': [7.0975, 4.9798],
            'emulsion_loss_modulus': [42, 31],
            'emulsion_storage_modulus': [13.823, 2.4437],
            'emulsion_tan_delta_v_e': [3.135, 12],
            'emulsion_visual_stability': ['Entrained', None],
            'emulsion_water_content': [39.787, 15.592],
            'method': ['13.02/x.x/M', '13.02/x.x/M'],
            'replicates': [6, 6, 6, 6, 6, 9, 6, 6, 6, 5, 6, 9],
            'standard_deviation': [7, 3, 6, 0.4, 1, 2.3,
                                   7, 0.96, 6.9, 2, 1.1, 1.8]
         }),
        ('2234', 4, {
            'conditions': {
                'emulsion_complex_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_complex_viscosity': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa.s',
                     'unit_type': 'dynamicviscosity',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa.s',
                     'unit_type': 'dynamicviscosity',
                     'converted': True}
                ],
                'emulsion_loss_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_storage_modulus': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': 'Pa',
                     'unit_type': 'pressure',
                     'converted': True}
                ],
                'emulsion_tan_delta_v_e': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'unit_type': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'unit_type': None,
                     'converted': True}
                ],
                'emulsion_visual_stability': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'unit_type': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'unit_type': None,
                     'converted': True}
                ],
                'emulsion_water_content': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': '%',
                     'unit_type': 'massfraction',
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': '%',
                     'unit_type': 'massfraction',
                     'converted': True}
                ],
                'method': [
                    {'condition': 'On the day of formation',
                     'ref_temp': None, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': None, 'unit': None,
                     'converted': True}
                ],
                'replicates': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}
                ],
                'standard_deviation': [
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'On the day of formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True},
                    {'condition': 'One week after formation',
                     'ref_temp': {'unit': 'C', 'value': 15.0}, 'unit': None,
                     'converted': True}
                ]
            },
            'emulsion_complex_modulus': [None, None],
            'emulsion_complex_viscosity': [None, None],
            'emulsion_loss_modulus': [None, None],
            'emulsion_storage_modulus': [None, None],
            'emulsion_tan_delta_v_e': [None, None],
            'emulsion_visual_stability': ['Did not form', None],
            'emulsion_water_content': [None, None],
            'method': [None, None],
            'replicates': [None, None, None, None, None, None,
                           None, None, None, None, None, None],
            'standard_deviation': [None, None, None, None, None, None,
                                   None, None, None, None, None, None]
         }),
    ])
    def test_emulsion(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].emulsions, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'dispersant_effectiveness': 45.851,
                     'method': 'ASTM F2059',
                     'replicates': 6,
                     'standard_deviation': 3.5196}),
        ('2713', 3, {'dispersant_effectiveness': '<10',
                     'method': 'ASTM F2059',
                     'replicates': 6,
                     'standard_deviation': None}),
    ])
    def test_chemical_dispersibility(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].chemical_dispersibility,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'method': 'ASTM D4294',
                     'replicates': 3,
                     'standard_deviation': 0,
                     'sulfur_content': 0.9}),
        ('2713', 3, {'method': 'ASTM D4294',
                     'replicates': 3,
                     'standard_deviation': 0.01,
                     'sulfur_content': 1.4}),
    ])
    def test_sulfur_content(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].sulfur_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'method': 'ASTM E203',
                     'replicates': 3,
                     'standard_deviation': 0.01,
                     'water_content': 0.27}),
        ('2713', 3, {'method': 'ASTM E203',
                     'replicates': 3,
                     'standard_deviation': 0,
                     'water_content': 0.1}),
    ])
    def test_water_content(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].water_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'method': '12.11/2.0/M',
                     'replicates': 3,
                     'standard_deviation': 0.13574,
                     'waxes': 3.9794}),
        ('2713', 3, {'method': '12.11/2.0/M',
                     'replicates': 3,
                     'standard_deviation': 0.39541,
                     'waxes': 6.0319}),
    ])
    def test_wax_content(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].wax_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'aromatics': 31.9,
                     'asphaltene': 3.9794,
                     'method': '12.11/3.0/M',
                     'replicates': [3, 3],
                     'resin': 6.4506,
                     'saturates': 57.9,
                     'standard_deviation': [0.21576, 0.13574]}),
        ('2713', 3, {'aromatics': 30.1,
                     'asphaltene': 7.7224,
                     'method': '12.11/3.0/M',
                     'replicates': [3, 3],
                     'resin': 10.705,
                     'saturates': 51.5,
                     'standard_deviation': [0.52482, 0.20592]}),
    ])
    def test_sara_total_fractions(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].sara_total_fractions,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {None: None}),
        ('561', 3, {None: None}),
    ])
    def test_benzene(self, rec, index, expected):
        """
        Note: The category header for the benzene groups no longer contains
              any data.  It's all in the other groups.
        """
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].benzene, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'benzene': 1883.6,
                    'ethylbenzene': 1199.7,
                    'm_p_xylene': 3092.5,
                    'o_xylene': 1619.2,
                    'toluene': 4173.3}),
        ('561', 3, {'benzene': 0,
                    'ethylbenzene': 0,
                    'm_p_xylene': 0,
                    'o_xylene': 0,
                    'toluene': 0}),
    ])
    def test_btex_group(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].btex_group, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'_1_2_3_trimethylbenzene': 489.79,
                    '_1_2_4_trimethylbenzene': 1760.5,
                    '_1_2_dimethyl_4_ethylbenzene': 458.33,
                    '_1_3_5_trimethylbenzene': 675.96,
                    '_1_methyl_2_isopropylbenzene': 52.882,
                    '_2_ethyltoluene': 549.75,
                    '_3_4_ethyltoluene': 1349.6,
                    'amylbenzene': 63.835,
                    'isobutylbenzene': 73.443,
                    'isopropylbenzene': 11968.0,
                    'method': '5.02/x.x/M',
                    'n_hexylbenzene': 83.745,
                    'propylebenzene': 711.48}),
        ('561', 3, {'_1_2_3_trimethylbenzene': 4.6633,
                    '_1_2_4_trimethylbenzene': 13.611,
                    '_1_2_dimethyl_4_ethylbenzene': 58.853,
                    '_1_3_5_trimethylbenzene': 2.1617,
                    '_1_methyl_2_isopropylbenzene': 1.4086,
                    '_2_ethyltoluene': 1.2805,
                    '_3_4_ethyltoluene': 1.8529,
                    'amylbenzene': 25.917,
                    'isobutylbenzene': 0.85681,
                    'isopropylbenzene': 0,
                    'method': '5.02/x.x/M',
                    'n_hexylbenzene': 75.861,
                    'propylebenzene': 0.35799}),
    ])
    def test_c4_c6_alkyl_benzenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].c4_c6_alkyl_benzenes,
                                     expected)

    @pytest.mark.skip
    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'c5_group': 49.414,
                    'c6_group': 54.823,
                    'c7_group': 29.202,
                    'n_c5': 16.689,
                    'n_c6': 9.194,
                    'n_c7': 5.0631,
                    'n_c8': 5.43}),
        ('561', 3, {'c5_group': None,
                    'c6_group': None,
                    'c7_group': None,
                    'n_c5': None,
                    'n_c6': None,
                    'n_c7': None,
                    'n_c8': 0}),
    ])
    def test_headspace_analysis(self, rec, index, expected):
        """
        Note: The April 2020 datasheet has no headspace information.
              We will skip this test for now.
        """
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].headspace_analysis,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'method': '5.03/x.x/M',
                     'resolved_peaks_tph': 9.0821,
                     'tah': 134.62,
                     'tah_tph': 45.006,
                     'tph': 299.0,
                     'tsh': 164.38,
                     'tsh_tph': 54.994}),
        ('2234', 3, {'method': '5.03/x.x/M',
                     'resolved_peaks_tph': 7.2719,
                     'tah': 155.18,
                     'tah_tph': 49.618,
                     'tph': 312.74,
                     'tsh': 157.56,
                     'tsh_tph': 50.382}),
    ])
    def test_chromatography(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].chromatography, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'f1': 15.584,
                     'f2': 50.056,
                     'f3': 193.13,
                     'f4': 40.226}),
        ('2234', 3, {'f1': 1.6231,
                     'f2': 28.16,
                     'f3': 251.51,
                     'f4': 31.447}),
    ])
    def test_ccme(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ccme, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'n_c10_to_n_c12': 10.82,
                     'n_c12_to_n_c16': 29.75,
                     'n_c16_to_n_c20': 30.84,
                     'n_c20_to_n_c24': 21.56,
                     'n_c24_to_n_c28': 16.03,
                     'n_c28_to_n_c34': 22.23,
                     'n_c34': 14.79,
                     'n_c8_to_n_c10': 18.35}),
        ('2234', 3, {'n_c10_to_n_c12': 0.69,
                     'n_c12_to_n_c16': 18.08,
                     'n_c16_to_n_c20': 37.54,
                     'n_c20_to_n_c24': 28.3,
                     'n_c24_to_n_c28': 22.05,
                     'n_c28_to_n_c34': 32.11,
                     'n_c34': 16.9,
                     'n_c8_to_n_c10': 1.89}),
    ])
    def test_ests_saturates(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ests_saturates, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'n_c10_to_n_c12': 2.17,
                     'n_c12_to_n_c16': 5.56,
                     'n_c16_to_n_c20': 17.05,
                     'n_c20_to_n_c24': 23.43,
                     'n_c24_to_n_c28': 23.11,
                     'n_c28_to_n_c34': 33,
                     'n_c34': 26.59,
                     'n_c8_to_n_c10': 3.72}),
        ('2234', 3, {'n_c10_to_n_c12': 0.95,
                     'n_c12_to_n_c16': 5.21,
                     'n_c16_to_n_c20': 20.95,
                     'n_c20_to_n_c24': 29.7,
                     'n_c24_to_n_c28': 30.45,
                     'n_c28_to_n_c34': 42.48,
                     'n_c34': 23.92,
                     'n_c8_to_n_c10': 1.51}),
    ])
    def test_ests_aromatics(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ests_aromatics, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'n_c10_to_n_c12': 14.17,
                     'n_c12_to_n_c16': 37.59,
                     'n_c16_to_n_c20': 48.43,
                     'n_c20_to_n_c24': 45.4,
                     'n_c24_to_n_c28': 40.4,
                     'n_c28_to_n_c34': 58.12,
                     'n_c34': 39.67,
                     'n_c8_to_n_c10': 15.24,
                     'total_tph_gc_detected_tph_undetected_tph': 690}),
        ('2234', 3, {'n_c10_to_n_c12': 1.97,
                     'n_c12_to_n_c16': 25.23,
                     'n_c16_to_n_c20': 59.07,
                     'n_c20_to_n_c24': 58.62,
                     'n_c24_to_n_c28': 54.19,
                     'n_c28_to_n_c34': 75.22,
                     'n_c34': 35.95,
                     'n_c8_to_n_c10': 2.5,
                     'total_tph_gc_detected_tph_undetected_tph': 540}),
    ])
    def test_ests_tph(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].ests_tph, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_n': 501.23,
                     'c1_n': 1377.4,
                     'c2_n': 2071.4,
                     'c3_n': 1808.6,
                     'c4_n': 960.67}),
        ('2713', 3, {'c0_n': 18.58,
                     'c1_n': 651.43,
                     'c2_n': 2074.0,
                     'c3_n': 2358.4,
                     'c4_n': 1361.2}),
    ])
    def test_naphthalenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].naphthalenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_p': 177.18,
                     'c1_p': 485.64,
                     'c2_p': 509.74,
                     'c3_p': 378.28,
                     'c4_p': 176.29}),
        ('2713', 3, {'c0_p': 258.95,
                     'c1_p': 698.43,
                     'c2_p': 772.55,
                     'c3_p': 591.44,
                     'c4_p': 273.87}),
    ])
    def test_phenanthrenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].phenanthrenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_d': 107.19,
                     'c1_d': 223.27,
                     'c2_d': 313.63,
                     'c3_d': 259.23}),
        ('2713', 3, {'c0_d': 155.02,
                     'c1_d': 325.05,
                     'c2_d': 466.15,
                     'c3_d': 415.56}),
    ])
    def test_dibenzothiophenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].dibenzothiophenes,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_f': 66.163,
                     'c1_f': 151.85,
                     'c2_f': 220.25,
                     'c3_f': 233.99}),
        ('2713', 3, {'c0_f': 87.95,
                     'c1_f': 223.17,
                     'c2_f': 333.75,
                     'c3_f': 341.1}),
    ])
    def test_fluorenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].fluorenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_b': 41.118,
                     'c1_b': 136.9,
                     'c2_b': 107.87,
                     'c3_b': 173.74,
                     'c4_b': 115.0}),
        ('2713', 3, {'c0_b': 62.143,
                     'c1_b': 211.19,
                     'c2_b': 127.96,
                     'c3_b': 262.16,
                     'c4_b': 170.6}),
    ])
    def test_benzonaphthothiophenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].benzonaphthothiophenes,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_c': 574.63,
                     'c1_c': 29.726,
                     'c2_c': 53.463,
                     'c3_c': 78.953}),
        ('2713', 3, {'c0_c': 834.06,
                     'c1_c': 44.888,
                     'c2_c': 84.313,
                     'c3_c': 118.69}),
    ])
    def test_chrysenes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].chrysenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'acenaphthene': 14.77,
                     'acenaphthylene': 13.582,
                     'anthracene': 3.3171,
                     'benz_a_anthracene': 2.8115,
                     'benzo_a_pyrene': 2.083,
                     'benzo_b_fluoranthene': 4.7402,
                     'benzo_e_pyrene': 7.5749,
                     'benzo_ghi_perylene': 2.9375,
                     'benzo_k_fluoranthene': 0,
                     'biphenyl': 125.19,
                     'dibenzo_ah_anthracene': 1.1867,
                     'fluoranthene': 5.1809,
                     'indeno_1_2_3_cd_pyrene': 0.55658,
                     'method': '5.03/x.x/M',
                     'perylene': 3.2858,
                     'pyrene': 15.784}),
        ('2713', 3, {'acenaphthene': 13.492,
                     'acenaphthylene': 13.539,
                     'anthracene': 4.1555,
                     'benz_a_anthracene': 2.9093,
                     'benzo_a_pyrene': 1.6596,
                     'benzo_b_fluoranthene': 5.183,
                     'benzo_e_pyrene': 8.116,
                     'benzo_ghi_perylene': 3.019,
                     'benzo_k_fluoranthene': 0,
                     'biphenyl': 124.33,
                     'dibenzo_ah_anthracene': 1.3269,
                     'fluoranthene': 5.519,
                     'indeno_1_2_3_cd_pyrene': 0.58979,
                     'method': '5.03/x.x/M',
                     'perylene': 3.9403,
                     'pyrene': 16.281}),
    ])
    def test_other_priority_pahs(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].other_priority_pahs,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c10': 3655.8,
                     'c11': 3208.2,
                     'c12': 3057.2,
                     'c13': 2850.1,
                     'c14': 840.11,
                     'c15': 2598.5,
                     'c16': 2198.8,
                     'c17': 2024.3,
                     'c18': 2092.9,
                     'c19': 1686.0,
                     'c20': 973.94,
                     'c21': 1578.6,
                     'c22': 1467.1,
                     'c23': 1405.6,
                     'c24': 1343.4,
                     'c25': 1278.9,
                     'c26': 1212.8,
                     'c27': 1152.1,
                     'c28': 1081.8,
                     'c29': 876.02,
                     'c30': 690.68,
                     'c31': 576.11,
                     'c32': 479.66,
                     'c33': 402.89,
                     'c34': 307.1,
                     'c35': 262.28,
                     'c36': 204.42,
                     'c37': 193.76,
                     'c38': 151.13,
                     'c39': 115.57,
                     'c40': 88.418,
                     'c41': 60.306,
                     'c42': 43.073,
                     'c43': None,
                     'c44': None,
                     'c8': None,
                     'c9': 4101.7,
                     'method': '5.03/x.x/M',
                     'phytane': 882.09,
                     'pristane': 1037.1}),
        ('2713', 3, {'c10': 0.48342,
                     'c11': 3.0091,
                     'c12': 307.84,
                     'c13': 1648.0,
                     'c14': 723.36,
                     'c15': 2569.6,
                     'c16': 2574.2,
                     'c17': 2574.1,
                     'c18': 2362.9,
                     'c19': 2235.4,
                     'c20': 1441.8,
                     'c21': 2102.9,
                     'c22': 1940.9,
                     'c23': 1900.6,
                     'c24': 1777.6,
                     'c25': 1713.7,
                     'c26': 1558.1,
                     'c27': 1582.8,
                     'c28': 1494.2,
                     'c29': 1196.7,
                     'c30': 992.82,
                     'c31': 826.83,
                     'c32': 685.72,
                     'c33': 622.51,
                     'c34': 479.11,
                     'c35': 416.92,
                     'c36': 334.49,
                     'c37': 327.34,
                     'c38': 246.1,
                     'c39': 223.67,
                     'c40': 151.73,
                     'c41': 103.79,
                     'c42': 79.647,
                     'c43': None,
                     'c44': None,
                     'c8': None,
                     'c9': 1.2005,
                     'method': '5.03/x.x/M',
                     'phytane': 1105.6,
                     'pristane': 1403.9}),
    ])
    def test_n_alkanes(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].n_alkanes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'_14b_h_17b_h_20_cholestane': 187.86,
                     '_14b_h_17b_h_20_ethylcholestane': 240.15,
                     '_14b_h_17b_h_20_methylcholestane': 151.53,
                     '_17a_h_22_29_30_trisnorhopane': 22.315,
                     '_18a_22_29_30_trisnorneohopane': 32.296,
                     '_30_31_bishomohopane_22r': 82.208,
                     '_30_31_bishomohopane_22s': 109.6,
                     '_30_31_trishomohopane_22r': 47.996,
                     '_30_31_trishomohopane_22s': 64.934,
                     '_30_homohopane_22r': 255.6,
                     '_30_homohopane_22s': 213.11,
                     '_30_norhopane': 27.1,
                     'c21_tricyclic_terpane': 35.308,
                     'c22_tricyclic_terpane': 16.578,
                     'c23_tricyclic_terpane': 106.74,
                     'c24_tricyclic_terpane': 55.274,
                     'hopane': 71.864,
                     'method': '5.03/x.x/M',
                     'pentakishomohopane_22r': 19.834,
                     'pentakishomohopane_22s': 30.081,
                     'tetrakishomohopane_22r': 31.932,
                     'tetrakishomohopane_22s': 49.561}),
        ('2234', 4, {'_14b_h_17b_h_20_cholestane': 234.6,
                     '_14b_h_17b_h_20_ethylcholestane': 304.77,
                     '_14b_h_17b_h_20_methylcholestane': 191.25,
                     '_17a_h_22_29_30_trisnorhopane': 23.623,
                     '_18a_22_29_30_trisnorneohopane': 35.934,
                     '_30_31_bishomohopane_22r': 105.7,
                     '_30_31_bishomohopane_22s': 141.89,
                     '_30_31_trishomohopane_22r': 60.458,
                     '_30_31_trishomohopane_22s': 85.826,
                     '_30_homohopane_22r': 320.93,
                     '_30_homohopane_22s': 271.87,
                     '_30_norhopane': 34.527,
                     'c21_tricyclic_terpane': 41.662,
                     'c22_tricyclic_terpane': 19.78,
                     'c23_tricyclic_terpane': 126.43,
                     'c24_tricyclic_terpane': 65.354,
                     'hopane': 89.128,
                     'method': '5.03/x.x/M',
                     'pentakishomohopane_22r': 22.688,
                     'pentakishomohopane_22s': 35.872,
                     'tetrakishomohopane_22r': 39.214,
                     'tetrakishomohopane_22s': 60.809}),
    ])
    def test_biomarkers(self, rec, index, expected):
        data, conditions, file_props = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, conditions, file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].biomarkers, expected)


class TestEnvCanadaRecordMapper(object):
    """
    Note: still building up the new version of the mapper
    """
    reader = EnvCanadaOilExcelFile(data_file)

    def deep_get(self, json_obj, attr_path):
        if isinstance(attr_path, str):
            attr_path = attr_path.split('.')

        if len(attr_path) > 1:
            return self.deep_get(json_obj[attr_path[0]], attr_path[1:])
        else:
            return json_obj[attr_path[0]]

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaRecordMapper()

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            _mapper = EnvCanadaRecordMapper(None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', {'oil_id': 'EC02713',
                  'metadata.name': 'Alaska North Slope [2015]',
                  'metadata.source_id': '2713',
                  'metadata.location': 'Alaska, USA',
                  'metadata.reference': {'reference': 'Personal communication '
                                                      'from Fatemeh Mirnaghi '
                                                      '(ESTS), '
                                                      'date: April 21, 2020.',
                                         'year': 2020},
                  'metadata.sample_date': '2015-03-22',
                  'metadata.product_type': 'Crude Oil NOS',
                  'metadata.API': 31.32,
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
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        mapper = EnvCanadaRecordMapper(parser)
        py_json = mapper.py_json()

        for k, v in expected.items():
            if v is not None:
                assert self.deep_get(py_json, k) == v

    def test_save_to_json(self):
        """
        Save an example .json file.  This is not so much a test, but a job
        to provide sample data that people can look at.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record('2234'))
        mapper = EnvCanadaRecordMapper(parser)
        py_json = mapper.py_json()

        py_json['status'] = []

        filename = 'EC-Example-Record.json'
        file_path = os.path.sep.join(
            adios_db.__file__.split(os.path.sep)[:-3] + ['examples', filename]
        )

        print(f'saving to: {file_path}')
        with open(file_path, 'w', encoding="utf-8") as fd:
            json.dump(py_json, fd, indent=4, sort_keys=True)


class TestEnvCanadaSampleMapper(object):
    """
    Note: still building up the new version of the mapper
    """
    reader = EnvCanadaOilExcelFile(data_file)

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaSampleMapper()

        with pytest.raises(TypeError):
            _mapper = EnvCanadaSampleMapper(None)

        with pytest.raises(TypeError):
            _mapper = EnvCanadaSampleMapper(None, None)

        mapper = EnvCanadaSampleMapper(None, None, None)

        with pytest.raises(AttributeError):
            mapper.dict()

    @pytest.mark.parametrize('oil_id', [
        '2713',
        '561',
    ])
    def test_init_valid(self, oil_id):
        """
        We are being fairly light on the parameter checking in our
        constructor.  So if no file props are passed in, we can still
        construct the parser, but accessing reference_date could raise
        a TypeError.
        This is because the reference_date will sometimes need the
        file props if the reference field contains no date information.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        mapper = EnvCanadaRecordMapper(parser)
        sub_mapper = mapper.sub_samples[0]

        assert type(sub_mapper) == EnvCanadaSampleMapper

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2713', 0, 'metadata', {'boiling_point_range': None,
                                 'fraction_weathered': {'unit': 'fraction',
                                                        'value': 0.0},
                                 'name': 'Fresh Oil Sample',
                                 'short_name': 'Fresh Oil',
                                 'sample_id': '2713.1'}),
        ('2713', -1, 'metadata', {'boiling_point_range': None,
                                  'fraction_weathered': {'unit': 'fraction',
                                                         'value': 0.3676},
                                  'name': '36.76% Evaporated',
                                  'short_name': '36.76% Evaporated',
                                  'sample_id': '2713.2.1'}),
        ('2713', 0, 'densities', [
            {'density': {'value': 0.8751, 'unit': 'g/mL',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'},
             'method': 'ASTM D5002'},
            {'density': {'value': 0.8639, 'unit': 'g/mL',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'},
             'method': 'ASTM D5002'}
         ]),
        ('2713', 0, 'dynamic_viscosities', [
            {'method': 'ASTM D7042',
             'ref_temp': {'value': 0.0, 'unit': 'C'},
             'viscosity': {'value': 17.92, 'unit': 'mPa.s',
                           'standard_deviation': 0.001, 'replicates': 3}},
            {'method': 'ASTM D7042',
             'ref_temp': {'unit': 'C', 'value': 15.0},
             'viscosity': {'value': 9.852, 'unit': 'mPa.s',
                           'standard_deviation': 0.0098, 'replicates': 3}}
         ]),
        ('2234', 3, 'dynamic_viscosities', [
            {'method': 'ESTS: 12.06/x.x/M',
             'ref_temp': {'unit': 'C', 'value': 0.0},
             'shear_rate': {'unit': '1/s', 'value': 0.01},
             'viscosity': {'value': 90000000, 'unit': 'mPa.s',
                           'standard_deviation': 2233500.0, 'replicates': 3}},
            {'method': 'ESTS: 12.06/x.x/M',
             'ref_temp': {'unit': 'C', 'value': 15.0},
             'shear_rate': {'unit': '1/s', 'value': 10.0},
             'viscosity': {'value': 1000000, 'unit': 'mPa.s',
                           'standard_deviation': 67002.0, 'replicates': 3}}
         ]),
        ('2713', 0, 'distillation_data', {
            'type': 'mass fraction',
            'method': 'Merged ASTM D7169 & ASTM D6730 mod.',
            'end_point': {'min_value': 720.0, 'max_value': None, 'unit': 'C'},
            'cuts': [
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 5},
                 'vapor_temp': {'unit': 'C', 'value': 60.3}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 10},
                 'vapor_temp': {'unit': 'C', 'value': 91.9}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 15},
                 'vapor_temp': {'unit': 'C', 'value': 119.4}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 20},
                 'vapor_temp': {'unit': 'C', 'value': 147.9}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 25},
                 'vapor_temp': {'unit': 'C', 'value': 180.6}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 30},
                 'vapor_temp': {'unit': 'C', 'value': 215.7}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 35},
                 'vapor_temp': {'unit': 'C', 'value': 247.7}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 40},
                 'vapor_temp': {'unit': 'C', 'value': 277.7}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 45},
                 'vapor_temp': {'unit': 'C', 'value': 308}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 50},
                 'vapor_temp': {'unit': 'C', 'value': 339.1}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 55},
                 'vapor_temp': {'unit': 'C', 'value': 371.2}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 60},
                 'vapor_temp': {'unit': 'C', 'value': 404.3}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 65},
                 'vapor_temp': {'unit': 'C', 'value': 436.3}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 70},
                 'vapor_temp': {'unit': 'C', 'value': 473.3}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 75},
                 'vapor_temp': {'unit': 'C', 'value': 516.4}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 80},
                 'vapor_temp': {'unit': 'C', 'value': 567.6}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 85},
                 'vapor_temp': {'unit': 'C', 'value': 622.6}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 90},
                 'vapor_temp': {'unit': 'C', 'value': 680.2}},
                {'fraction': {'unit': '%', 'unit_type': 'massfraction', 'value': 0.0},
                 'vapor_temp': {'unit': 'C', 'value': -11.7}}
            ]
         }),
        ('561', 0, 'pour_point', None),
        ('2713', 0, 'pour_point', {'method': 'ASTM D97',
                                   'measurement': {'value': -51, 'unit': 'C',
                                                   'standard_deviation': 2,
                                                   'replicates': 3}}
         ),
        ('2713', 0, 'flash_point', None),
        ('2713', 1, 'flash_point', {'method': 'ASTM D7094',
                                    'measurement': {'value': 23.33,
                                                    'unit': 'C',
                                                    'standard_deviation': 1.15,
                                                    'replicates': 3}}
         ),
        ('2713', 0, 'interfacial_tensions', [
            {'interface': 'air',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 27.14, 'unit': 'mN/m',
                         'standard_deviation': 0.18, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             },
            {'interface': 'water',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 21.32, 'unit': 'mN/m',
                         'standard_deviation': 0.27, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             },
            {'interface': 'seawater',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 19.75, 'unit': 'mN/m',
                         'standard_deviation': 0.35, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             },
            {'interface': 'air',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 27.69, 'unit': 'mN/m',
                         'standard_deviation': 0.82, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}},
            {'interface': 'water',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 24.09, 'unit': 'mN/m',
                         'standard_deviation': 0.17, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}
             },
            {'interface': 'seawater',
             'method': 'ESTS: 12.12/x.x/M',
             'tension': {'value': 22.81, 'unit': 'mN/m',
                         'standard_deviation': 0.18, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}
             },
         ]),
        ('2713', 0, 'dispersibilities', [
            {'dispersant': 'Corexit 9500',
             'method': 'Swirling Flask Test (ASTM F2059)',
             'effectiveness': {'value': 45.851, 'unit': '%',
                               'standard_deviation': 3.5196,
                               'replicates': 6}}
         ]),
        ('2234', 0, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0},
             'method': 'ESTS: 13.02/x.x/M',
             'ref_temp': {'unit': 'C', 'value': 15.0},
             'visual_stability': 'Entrained',
             'complex_modulus': {'value': 45, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 7, 'replicates': 6},
             'complex_viscosity': {'value': 7.0975, 'unit': 'Pa.s',
                                   'standard_deviation': 1, 'replicates': 6},
             'loss_modulus': {'value': 42, 'unit': 'Pa',
                              'unit_type': 'pressure',
                              'standard_deviation': 6, 'replicates': 6},
             'storage_modulus': {'value': 13.823, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 3, 'replicates': 6},
             'tan_delta_v_e': {'value': 3.135, 'unit': None,
                               'unit_type': 'unitless',
                               'standard_deviation': 0.4, 'replicates': 6},
             'water_content': {'value': 39.787, 'unit': '%',
                               'standard_deviation': 2.3, 'replicates': 9}},
            {'age': {'unit': 'day', 'value': 7},
             'method': 'ESTS: 13.02/x.x/M',
             'ref_temp': {'unit': 'C', 'value': 15.0},
             'visual_stability': None,
             'complex_modulus': {'value': 31, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 7, 'replicates': 6},
             'complex_viscosity': {'value': 4.9798, 'unit': 'Pa.s',
                                   'standard_deviation': 1.1, 'replicates': 6},
             'loss_modulus': {'value': 31, 'unit': 'Pa',
                              'unit_type': 'pressure',
                              'standard_deviation': 6.9, 'replicates': 6},
             'storage_modulus': {'value': 2.4437, 'unit': 'Pa',
                                 'unit_type': 'pressure',
                                 'standard_deviation': 0.96, 'replicates': 6},
             'tan_delta_v_e': {'value': 12, 'unit': None,
                               'unit_type': 'unitless',
                               'standard_deviation': 2, 'replicates': 5},
             'water_content': {'value': 15.592, 'unit': '%',
                               'standard_deviation': 1.8, 'replicates': 9}}
         ]),
        ('2713', 0, 'SARA', {
            'method': 'ESTS: 12.11/3.0/M',
            'aromatics': {'value': 31.9, 'unit': '%',
                          'standard_deviation': 0.21576,
                          'replicates': 3},
            'asphaltenes': {'value': 3.9794, 'unit': '%',
                            'standard_deviation': 0.13574,
                            'replicates': 3},
            'resins': {'value': 6.4506, 'unit': '%',
                       'standard_deviation': 0.21576,
                       'replicates': 3},
            'saturates': {'value': 57.9, 'unit': '%',
                          'standard_deviation': 0.21576,
                          'replicates': 3}
         }),
    ])
    def test_attribute(self, oil_id, index, attr, expected):
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        assert getattr(sub_mapper, attr) == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2234', 0, 'compounds', {
            'list_size': 91,
            'compound_attrs': ('name', 'method', 'groups', 'measurement'),
            'total_groups': {
                'Alkylated Aromatic Hydrocarbons',
                'Biomarkers',
                'n-Alkanes',
            }
         }),
        ('561', 0, 'compounds', {
            'list_size': 114,
            'compound_attrs': ('name', 'method', 'groups', 'measurement'),
            'total_groups': {
                'Alkylated Aromatic Hydrocarbons',
                'C4-C6 Alkyl Benzenes',
                'Biomarkers',
                'BTEX group',
                'n-Alkanes',
            }
         }),
        ('2234', 0, 'bulk_composition', {
            'list_size': 9,
            'compound_attrs': ('name', 'method', 'measurement'),
            'total_groups': None
         }),
        # headspace is no longer included in the datasheet
        # ('2234', 0, 'headspace_analysis', {
        #     'list_size': 0,
        #     'compound_attrs': ('name', 'method', 'groups', 'measurement'),
        #     'total_groups': set()
        #  }),
        # ('561', 0, 'headspace_analysis', {
        #     'list_size': 7,
        #     'compound_attrs': ('name', 'method', 'groups', 'measurement'),
        #     'total_groups': {
        #         'Headspace Analysis (mg/g oil) (ESTS 2002b):'
        #     }
        #  }),
    ])
    def test_compound_list(self, oil_id, index, attr, expected):
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        compounds = getattr(sub_mapper, attr)

        # We won't be checking every single compound since there are typically
        # over one hundred to check.  We will verify general properties of our
        # compound list though
        assert type(compounds) == list
        assert len(compounds) == expected['list_size']

        for c in compounds:
            for attr in expected['compound_attrs']:
                assert attr in c

            for attr in ('value', 'unit', 'unit_type'):
                assert attr in c['measurement']

        if expected['total_groups'] is not None:
            total_groups = set([sub for c in compounds for sub in c['groups']])
            assert total_groups == expected['total_groups']

    @pytest.mark.parametrize('oil_id, index, expected', [
        ('2234', 0, {
            'fractions': (15.584, 50.056, 193.13, 40.226),
         }),
        ('561', 0, {
            'fractions': (67.75, 170.81, 302.21, 59.841),
         }),
    ])
    def test_ccme(self, oil_id, index, expected):
        """
        CCME object is a struct.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        ccme = sub_mapper.CCME

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
        ('561', 0, {
            'list_sizes': [0, 0, 0],
         }),
    ])
    def test_ests_fractions(self, oil_id, index, expected):
        """
        ESTS_hydrocarbon_fractions object is a struct consisting of
        attributes that are compound lists.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        ests_fractions = sub_mapper.ESTS_hydrocarbon_fractions

        assert type(ests_fractions) == dict

        assert expected['list_sizes'] == [len(ests_fractions[attr]) for attr in
                                          ('saturates',
                                           'aromatics',
                                           'GC_TPH')]

    @pytest.mark.parametrize('oil_id, index', [
        ('2234', 0),
        ('561', 0),
    ])
    def test_physical_properties(self, oil_id, index):
        """
        CCME object is a hybrid of struct attributes with a few
        compound lists thrown in.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        phys = sub_mapper.physical_properties

        assert type(phys) == dict

        # env canada has no kinematic viscosities
        for attr in ('pour_point', 'flash_point',
                     'densities', 'dynamic_viscosities',
                     'interfacial_tension_air',
                     'interfacial_tension_water',
                     'interfacial_tension_seawater'):
            assert attr in phys

    @pytest.mark.parametrize('oil_id, index, attrs', [
        ('2234', 0, ('adhesion', 'dispersibilities', 'emulsions',
                     'ests_evaporation_test')),
        ('506', 0, ('adhesion', 'dispersibilities', 'emulsions',
                    'ests_evaporation_test')),
        ('561', 0, ('adhesion', 'dispersibilities', 'emulsions',
                    'ests_evaporation_test')),
    ])
    def test_environmental_behavior(self, oil_id, index, attrs):
        """
        CCME object is a hybrid of struct attributes with a few
        compound lists thrown in.
        """
        parser = EnvCanadaRecordParser(*self.reader.get_record(oil_id))
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        env = sub_mapper.environmental_behavior

        assert type(env) == dict

        # env canada has no kinematic viscosities
        for attr in attrs:
            assert attr in env
