'''
    tests of the Environment Canada data import modules

    As complete as possible, because we want to test for correctness,
    and we also want to document how it works.
    Either we test it correctly, or we test it in an episodic manner on the
    real dataset.
'''
from datetime import datetime
from pytz import timezone
from pathlib import Path

import pytest
import numpy as np

from openpyxl.utils.exceptions import InvalidFileException

from oil_database.data_sources.env_canada import (EnvCanadaOilExcelFile,
                                                  EnvCanadaRecordParser,
                                                  EnvCanadaRecordMapper,
                                                  EnvCanadaSampleMapper)

from pprint import pprint
from builtins import isinstance

example_dir = Path(__file__).resolve().parent / "example_data"
example_index = example_dir / "index.txt"
data_file = example_dir / "EnvCanadaTestSet.xlsx"


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
        assert reader.file_props['name'] == 'EnvCanadaTestSet.xlsx'
        assert reader.file_props['creator'] == 'Mirnaghi,Fatemeh [NCR]'

        # We should have five oil records
        assert reader.col_indexes == {'2234': [2, 3, 4, 5, 6],
                                      '2713': [7, 8, 9, 10],
                                      '540': [11, 12],
                                      '506': [13, 14, 15, 16],
                                      '561': [17, 18, 19, 20]}

        # There are literally hundreds of fields here, so let's just check
        # some of the individual category/field combinations
        assert reader.field_indexes[None]['Oil'] == [0]
        assert reader.field_indexes[None]['Weathered %:'] == [5]

        # the last row in our spreadsheet
        assert (reader.field_indexes
                ['Biomarkers (µg/g) (ESTS 2002a):']
                ['14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)']) == [341]

    def test_get_record(self):
        reader = EnvCanadaOilExcelFile(data_file)

        rec = reader.get_record('2234')

        # There are literally hundreds of fields here, so let's just check
        # some of the individual category/field combinations
        assert rec[None]['Oil'] == ['Access West Winter Blend ',
                                    None, None, None, None]
        assert rec[None]['Weathered %:'] == [0, 0.0853, 0.1686, 0.2534, 0.2645]

        # the last row in our spreadsheet
        assert np.allclose(rec
                           ['Biomarkers (µg/g) (ESTS 2002a):']
                           ['14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)'],
                           [240.14792754496634,
                            254.44341921951164,
                            278.77753706501784,
                            291.54103598970795,
                            304.76883967832725])

    def test_get_records(self):
        reader = EnvCanadaOilExcelFile(data_file)

        recs = list(reader.get_records())

        # five records in our test file
        assert len(recs) == 5

        for r in recs:
            # each item coming from records() is a record set containing
            # record data and file props
            assert len(r) == 2


class TestEnvCanadaRecordParser(object):
    reader = EnvCanadaOilExcelFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaRecordParser()

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _parser = EnvCanadaRecordParser(None, None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', 2016),
        pytest.param('2234', 2017,
                     marks=pytest.mark.raises(exception=TypeError)),
    ])
    def test_init_valid_data_arg(self, oil_id, expected):
        '''
            We are being fairly light on the parameter checking in our
            constructor.  So if no file props are passed in, we can still
            construct the parser, but accessing reference_date could raise
            a TypeError.
            This is because the reference_date will sometimes need the
            file props if the reference field contains no date information.
        '''
        data = self.reader.get_record(oil_id)
        parser = EnvCanadaRecordParser(data, None)  # should construct fine

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', 2016),
        ('2234', 2017),
    ])
    def test_init_valid_data_and_file_props(self, oil_id, expected):
        '''
            The reference_date will sometimes need the file props if the
            reference field contains no date information.  check that the
            file props are correctly parsed.
        '''
        data = self.reader.get_record(oil_id)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        assert parser.reference['year'] == expected

    @pytest.mark.parametrize('label, expected', [
        ('A Label', 'a_label'),
        ('0.0', '_0_0'),
        ('Density 5 ̊C (g/mL)', 'density_5_c_g_ml'),
        ('14ß(H),17ß(H)-20-Ethylcholestane(C29αßß)',
         '_14ss_h_17ss_h_20_ethylcholestane_c29assss'),
    ])
    def test_slugify(self, label, expected):
        data = self.reader.get_record('2234')
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        assert parser.slugify(label) == expected

    @pytest.mark.parametrize('path, expected', [
        ('gc_total_aromatic_hydrocarbon',
         'GC-TAH (mg/g Oil) (ESTS 2002a):'),
        ('gc_total_aromatic_hydrocarbon.tah',
         'Gas Chromatography-Total aromatic hydrocarbon (GC-TAH)'),
        (['gc_total_aromatic_hydrocarbon', 'tah'],
         'Gas Chromatography-Total aromatic hydrocarbon (GC-TAH)'),
        pytest.param('bogus', 'does not matter',
                     marks=pytest.mark.raises(exception=KeyError)),
        pytest.param('gc_total_aromatic_hydrocarbon.bogus', 'does not matter',
                     marks=pytest.mark.raises(exception=KeyError)),
    ])
    def test_get_label(self, path, expected):
        data = self.reader.get_record('2234')
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        assert parser.get_label(path) == expected

    @pytest.mark.parametrize('rec, attr, expected', [
        ('2234', 'name', 'Access West Winter Blend'),
        ('2234', 'oil_id', 'EC002234'),
        ('2234', 'ests_codes', ['2234.1.1 A', '2234.1.4.1 ', '2234.1.3.1 ',
                                '2234.1.2.1 ', '2234.1.5.1 ']),
        ('2234', 'weathering', [0.0, 0.0853, 0.1686, 0.2534, 0.2645]),
        ('2713', 'reference', {'reference': 'Hollebone, 2016. ',
                               'year': 2016}),
        ('2234', 'sample_date', datetime(2013, 4, 8, 0, 0)),
        ('2234', 'comments', 'Via  CanmetENERGY, Natural Resources Canada'),
        ('2234', 'location', 'Alberta, Canada'),
        ('2234', 'product_type', 'crude'),
        ('540', 'product_type', 'refined'),
    ])
    def test_attrs(self, rec, attr, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        assert getattr(parser, attr) == expected

    @pytest.mark.parametrize('rec, attr, index, expected', [
        ('2234', 'api_gravity.gravity', 0, 20.93),
        ('2234', 'api_gravity.gravity', 4, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, 240.147),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, 304.768),
    ])
    def test_vertical_slice(self, rec, attr, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        subsample = parser.vertical_slice(index)

        l1, l2 = attr.split('.')  # two dotted levels
        assert np.isclose(subsample[l1][l2], expected)

    @pytest.mark.parametrize('rec, attr, index, default, expected', [
        ('2234', 'api_gravity.gravity', 0, None, 20.93),
        ('2234', 'api_gravity.gravity', 4, None, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, None,
         240.147),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, None,
         304.768),
        ('2234', 'bogus.bogus', 0, 0, 0),
    ])
    def test_samples(self, rec, attr, index, default, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].deep_get(attr, default=default),
                           expected)


class TestEnvCanadaSampleParser(object):
    reader = EnvCanadaOilExcelFile(data_file)

    @pytest.mark.parametrize('rec, attr, index, default, expected', [
        ('2234', 'api_gravity.gravity', 0, None, 20.93),
        ('2234', 'api_gravity.gravity', 4, None, 8.01),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 0, None,
         240.147),
        ('2234', 'biomarkers._14b_h_17b_h_20_ethylcholestane', 4, None,
         304.768),
        ('2234', 'bogus.bogus', 0, 0, 0),
    ])
    def test_deep_get(self, rec, attr, index, default, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].deep_get(attr, default=default),
                           expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, 20.93),
        ('2234', 4, 8.01),
    ])
    def test_api(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)

        assert np.allclose(samples[index].api, expected)

    def compare_expected(self, value, expected):
        '''
            compare a dict value to an expected dict
        '''
        if isinstance(value, list):
            return all([self.compare_expected(*args)
                        for args in zip(value, expected)])
        else:
            for k, v in value.items():
                # wouldn't it be nice if np.isclose could handle things like
                # strings and NoneTypes?
                if v is None or isinstance(v, str):
                    return v == expected[k]
                elif isinstance(v, list):
                    return np.allclose([v_i for v_i in v if v_i is not None],
                                       [v_i for v_i in expected[k]
                                        if v_i is not None])
                else:
                    return np.allclose(v, expected[k])

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'density_15_c': 0.92526,
                     'standard_deviation': [0.000509139, 0.000337704],
                     'replicates': [3, 3],
                     'density_0_c': 0.939878,
                     'density_5_c': None}),
        ('2234', 4, {'density_15_c': 1.01404,
                     'standard_deviation': [1.52752e-06, 4.50924e-06],
                     'replicates': [3, 3],
                     'density_0_c': 1.02106,
                     'density_5_c': None}),
    ])
    def test_densities(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)

        assert self.compare_expected(samples[index].densities, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'method': 'ESTS 2001',
                     'replicates': [3, 3],
                     'standard_deviation': [8.27103, 24.4404],
                     'viscosity_at_0_c': 1300,
                     'viscosity_at_15_c': 350,
                     'viscosity_at_5_c': None}),
        ('2234', 4, {'method': 'ESTS 2001',
                     'replicates': [3, 3],
                     'standard_deviation': [119302.13744941873, None],
                     'viscosity_at_0_c': '>1E+8',
                     'viscosity_at_15_c': 7909000,
                     'viscosity_at_5_c': None}),
    ])
    def test_dvis(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].dvis)

        assert self.compare_expected(samples[index].dvis, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'ift_0_c_oil_air': 31.1466,
                     'ift_0_c_oil_seawater': 24.9599,
                     'ift_0_c_oil_water': 24.78,
                     'ift_15_c_oil_air': 30.1966,
                     'ift_15_c_oil_seawater': 23.8266,
                     'ift_15_c_oil_water': 24.2366,
                     'ift_5_c_oil_air': None,
                     'ift_5_c_oil_seawater': None,
                     'ift_5_c_oil_water': None,
                     'method': ['ESTS 2008', 'ESTS 2008'],
                     'replicates': [None, None, None, None, None, None],
                     'standard_deviation': [0.113724,
                                            0.0450924,
                                            0.0208166,
                                            0.150443,
                                            0.134536,
                                            0.246373]}),
        ('2234', 4, {'ift_0_c_oil_air': 'Too Viscous',
                     'ift_0_c_oil_seawater': 'Too Viscous',
                     'ift_0_c_oil_water': 'Too Viscous',
                     'ift_15_c_oil_air': 'Too Viscous',
                     'ift_15_c_oil_seawater': 'Too Viscous',
                     'ift_15_c_oil_water': 'Too Viscous',
                     'ift_5_c_oil_air': None,
                     'ift_5_c_oil_seawater': None,
                     'ift_5_c_oil_water': None,
                     'method': ['ESTS 2008', 'ESTS 2008'],
                     'replicates': [None, None, None, None, None, None],
                     'standard_deviation': ['Too Viscous',
                                            'Too Viscous',
                                            'Too Viscous',
                                            'Too Viscous',
                                            'Too Viscous',
                                            'Too Viscous']}),
    ])
    def test_ift(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].ift)

        assert self.compare_expected(samples[index].ift, expected)

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
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].flash_point)

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
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].pour_point)

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
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].boiling_point_distribution)

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
                    'method': 'ESTS 2001',
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
                    'method': 'ESTS 2001',
                    'temperature_c': None}),
    ])
    def test_boiling_point_cumulative_fraction(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].boiling_point_cumulative_fraction)

        assert self.compare_expected(samples[index]
                                     .boiling_point_cumulative_fraction,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'adhesion': 18.03,
                     'replicates': 3,
                     'standard_deviation': 1.05}),
        ('2713', 3, {'adhesion': 56.39,
                     'replicates': 3,
                     'standard_deviation': 3.09}),
    ])
    def test_adhesion(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].adhesion)

        assert self.compare_expected(samples[index].adhesion, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'a_for_ev_a_b_ln_t_c': None,
                     'a_for_ev_a_bt_ln_t': 1.72,
                     'a_for_ev_a_bt_sqrt_t': None,
                     'b_for_ev_a_b_ln_t_c': None,
                     'b_for_ev_a_bt_ln_t': 0.045,
                     'b_for_ev_a_bt_sqrt_t': None,
                     'c_for_ev_a_b_ln_t_c': None}),
        ('2234', 4, {'a_for_ev_a_b_ln_t_c': None,
                     'a_for_ev_a_bt_ln_t': None,
                     'a_for_ev_a_bt_sqrt_t': None,
                     'b_for_ev_a_b_ln_t_c': None,
                     'b_for_ev_a_bt_ln_t': None,
                     'b_for_ev_a_bt_sqrt_t': None,
                     'c_for_ev_a_b_ln_t_c': None}),
    ])
    def test_evaporation_eqs(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].evaporation_eqs)

        assert self.compare_expected(samples[index].evaporation_eqs, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, [{'complex_modulus_pa': 40,
                      'complex_viscosity_pa_s': 7.09749,
                      'loss_modulus_pa': 40,
                      'replicates': [6, 9],
                      'standard_deviation': [18, 6, 17, 1.2, 2.9, 2.3],
                      'storage_modulus_pa': 13.8228,
                      'tan_delta_v_e': 3.135,
                      'visual_stability': 'Entrained',
                      'water_content_w_w': 39.7866},
                     {'complex_modulus_pa': 30,
                      'complex_viscosity_pa_s': 4.97983,
                      'loss_modulus_pa': 30,
                      'replicates': [6, 9],
                      'standard_deviation': [7, 0.96, 6.9, 4.1, 1.1, 1.8],
                      'storage_modulus_pa': 2.44366,
                      'tan_delta_v_e': 13.8833,
                      'visual_stability': None,
                      'water_content_w_w': 15.5922}]),
        ('2234', 4, [{'complex_modulus_pa': None,
                      'complex_viscosity_pa_s': None,
                      'loss_modulus_pa': None,
                      'replicates': [None, None],
                      'standard_deviation': [None, None, None, None, None,
                                             None],
                      'storage_modulus_pa': None,
                      'tan_delta_v_e': None,
                      'visual_stability': 'Did not form',
                      'water_content_w_w': None},
                     {'complex_modulus_pa': None,
                      'complex_viscosity_pa_s': None,
                      'loss_modulus_pa': None,
                      'replicates': [None, None],
                      'standard_deviation': [None, None, None, None, None,
                                             None],
                      'storage_modulus_pa': None,
                      'tan_delta_v_e': None,
                      'visual_stability': None,
                      'water_content_w_w': None}]),
    ])
    def test_emulsion(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(list(samples[index].emulsion))

        assert self.compare_expected(list(samples[index].emulsion), expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'dispersant_effectiveness': 45.8513,
                     'replicates': 6,
                     'standard_deviation': 3.51957}),
        ('2713', 3, {'dispersant_effectiveness': '<10',
                     'replicates': 6,
                     'standard_deviation': 1.61954}),
    ])
    def test_chemical_dispersibility(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].chemical_dispersibility)

        assert self.compare_expected(samples[index].chemical_dispersibility,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'replicates': 3,
                     'standard_deviation': 0,
                     'sulfur_content': 0.9}),
        ('2713', 3, {'replicates': 3,
                     'standard_deviation': 0.01,
                     'sulfur_content': 1.4}),
    ])
    def test_sulfur_content(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].sulfur_content)

        assert self.compare_expected(samples[index].sulfur_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'replicates': 3,
                     'standard_deviation': 0.01,
                     'water_content': 0.27}),
        ('2713', 3, {'replicates': 3,
                     'standard_deviation': 0,
                     'water_content': 0.1}),
    ])
    def test_water_content(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].water_content)

        assert self.compare_expected(samples[index].water_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'replicates': 3,
                     'standard_deviation': 0.135739,
                     'waxes': 3.97938}),
        ('2713', 3, {'replicates': 3,
                     'standard_deviation': 0.395413,
                     'waxes': 6.03187}),
    ])
    def test_wax_content(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].wax_content)

        assert self.compare_expected(samples[index].wax_content, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'aromatics': 31.9,
                     'asphaltene': 3.97938,
                     'method': [None, 'ESTS 2014'],
                     'replicates': [3, 3],
                     'resin': 6.45061,
                     'saturates': 57.9,
                     'standard_deviation': [0.215758, 0.135739]}),
        ('2713', 3, {'aromatics': 30.1,
                     'asphaltene': 7.72244,
                     'method': [None, 'ESTS 2014'],
                     'replicates': [3, 3],
                     'resin': 10.7051,
                     'saturates': 51.5,
                     'standard_deviation': [0.524822, 0.205916]}),
    ])
    def test_sara_total_fractions(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].sara_total_fractions)

        assert self.compare_expected(samples[index].sara_total_fractions,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'benzene': 1883.61}),
        ('561', 3, {'benzene': 0}),
    ])
    def test_benzene(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].benzene)

        assert self.compare_expected(samples[index].benzene, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'ethylbenzene': 1199.7,
                    'm_p_xylene': 3092.54,
                    'o_xylene': 1619.17,
                    'toluene': 4173.27}),
        ('561', 3, {'ethylbenzene': 0,
                    'm_p_xylene': 0,
                    'o_xylene': 0,
                    'toluene': 0}),
    ])
    def test_btex_group(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].btex_group)

        assert self.compare_expected(samples[index].btex_group, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'_1_2_3_trimethylbenzene': 489.791,
                    '_1_2_4_trimethylbenzene': 1760.45,
                    '_1_2_dimethyl_4_ethylbenzene': 458.328,
                    '_1_3_5_trimethylbenzene': 675.962,
                    '_1_methyl_2_isopropylbenzene': 52.8815,
                    '_2_ethyltoluene': 549.752,
                    '_3_4_ethyltoluene': 1349.57,
                    'amylbenzene': 63.835,
                    'isobutylbenzene': 73.4434,
                    'isopropylbenzene': 11968.3,
                    'n_hexylbenzene': 83.7454,
                    'propylebenzene': 711.483}),
        ('561', 3, {'_1_2_3_trimethylbenzene': 4.6633,
                    '_1_2_4_trimethylbenzene': 13.6106,
                    '_1_2_dimethyl_4_ethylbenzene': 58.8531,
                    '_1_3_5_trimethylbenzene': 2.16171,
                    '_1_methyl_2_isopropylbenzene': 1.40862,
                    '_2_ethyltoluene': 1.2805,
                    '_3_4_ethyltoluene': 1.85289,
                    'amylbenzene': 25.917,
                    'isobutylbenzene': 0.856811,
                    'isopropylbenzene': 0,
                    'n_hexylbenzene': 75.8609,
                    'propylebenzene': 0.35799}),
    ])
    def test_c4_c6_alkyl_benzenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].c4_c6_alkyl_benzenes)

        assert self.compare_expected(samples[index].c4_c6_alkyl_benzenes,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('561', 0, {'c5_group': 49.414,
                    'c6_group': 54.8234,
                    'c7_group': 29.2017,
                    'n_c5': 16.689,
                    'n_c6': 9.19396,
                    'n_c7': 5.06306,
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
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].headspace_analysis)

        assert self.compare_expected(samples[index].headspace_analysis,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'resolved_peaks_tph': 9.08211,
                     'tah': 134.619,
                     'tah_tph': 45.0063,
                     'tph': 298.995,
                     'tsh': 164.375,
                     'tsh_tph': 54.9936}),
        ('2234', 3, {'resolved_peaks_tph': 7.27187,
                     'tah': 155.182,
                     'tah_tph': 49.6184,
                     'tph': 312.742,
                     'tsh': 157.56,
                     'tsh_tph': 50.3815}),
    ])
    def test_chromatography(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].chromatography)

        assert self.compare_expected(samples[index].chromatography, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'f1': 15.5835,
                     'f2': 50.0558,
                     'f3': 193.13,
                     'f4': 40.2255}),
        ('2234', 3, {'f1': 1.62313,
                     'f2': 28.1604,
                     'f3': 251.512,
                     'f4': 31.4471}),
    ])
    def test_ccme(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].ccme)

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
    def test_ccme_f1(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].ccme_f1)

        assert self.compare_expected(samples[index].ccme_f1, expected)

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
    def test_ccme_f2(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].ccme_f2)

        assert self.compare_expected(samples[index].ccme_f2, expected)

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
    def test_ccme_tph(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].ccme_tph)

        assert self.compare_expected(samples[index].ccme_tph, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_n': 501.23,
                     'c1_n': 1377.4,
                     'c2_n': 2071.42,
                     'c3_n': 1808.57,
                     'c4_n': 960.667}),
        ('2713', 3, {'c0_n': 18.5797,
                     'c1_n': 651.428,
                     'c2_n': 2074.01,
                     'c3_n': 2358.35,
                     'c4_n': 1361.21}),
    ])
    def test_naphthalenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].naphthalenes)

        assert self.compare_expected(samples[index].naphthalenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_p': 177.176,
                     'c1_p': 485.636,
                     'c2_p': 509.739,
                     'c3_p': 378.276,
                     'c4_p': 176.293}),
        ('2713', 3, {'c0_p': 258.948,
                     'c1_p': 698.425,
                     'c2_p': 772.550,
                     'c3_p': 591.441,
                     'c4_p': 273.867}),
    ])
    def test_phenanthrenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].phenanthrenes)

        assert self.compare_expected(samples[index].phenanthrenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_d': 107.188,
                     'c1_d': 223.271,
                     'c2_d': 313.629,
                     'c3_d': 259.228}),
        ('2713', 3, {'c0_d': 155.018,
                     'c1_d': 325.054,
                     'c2_d': 466.152,
                     'c3_d': 415.56}),
    ])
    def test_dibenzothiophenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].dibenzothiophenes)

        assert self.compare_expected(samples[index].dibenzothiophenes,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_f': 66.1629,
                     'c1_f': 151.851,
                     'c2_f': 220.253,
                     'c3_f': 233.985}),
        ('2713', 3, {'c0_f': 87.9502,
                     'c1_f': 223.168,
                     'c2_f': 333.751,
                     'c3_f': 341.102}),
    ])
    def test_fluorenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].fluorenes)

        assert self.compare_expected(samples[index].fluorenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_b': 41.1182,
                     'c1_b': 136.904,
                     'c2_b': 107.872,
                     'c3_b': 173.735,
                     'c4_b': 114.996}),
        ('2713', 3, {'c0_b': 62.1425,
                     'c1_b': 211.189,
                     'c2_b': 127.962,
                     'c3_b': 262.164,
                     'c4_b': 170.599}),
    ])
    def test_benzonaphthothiophenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].benzonaphthothiophenes)

        assert self.compare_expected(samples[index].benzonaphthothiophenes,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c0_c': 574.627,
                     'c1_c': 29.7263,
                     'c2_c': 53.4625,
                     'c3_c': 78.9531}),
        ('2713', 3, {'c0_c': 834.058,
                     'c1_c': 44.8881,
                     'c2_c': 84.313,
                     'c3_c': 118.691}),
    ])
    def test_chrysenes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].chrysenes)

        assert self.compare_expected(samples[index].chrysenes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'acenaphthene': 14.7703,
                     'acenaphthylene': 13.5817,
                     'anthracene': 3.31707,
                     'benz_a_anthracene': 2.81146,
                     'benzo_a_pyrene': 2.08304,
                     'benzo_b_fluoranthene': 4.74017,
                     'benzo_e_pyrene': 7.57494,
                     'benzo_ghi_perylene': 2.93751,
                     'benzo_k_fluoranthene': 0,
                     'biphenyl': 125.193,
                     'dibenzo_ah_anthracene': 1.1867,
                     'fluoranthene': 5.18091,
                     'indeno_1_2_3_cd_pyrene': 0.55658,
                     'perylene': 3.28575,
                     'pyrene': 15.7843}),
        ('2713', 3, {'acenaphthene': 13.4921,
                     'acenaphthylene': 13.5393,
                     'anthracene': 4.15553,
                     'benz_a_anthracene': 2.90932,
                     'benzo_a_pyrene': 1.65962,
                     'benzo_b_fluoranthene': 5.18296,
                     'benzo_e_pyrene': 8.11601,
                     'benzo_ghi_perylene': 3.01896,
                     'benzo_k_fluoranthene': 0,
                     'biphenyl': 124.326,
                     'dibenzo_ah_anthracene': 1.32685,
                     'fluoranthene': 5.519,
                     'indeno_1_2_3_cd_pyrene': 0.58978,
                     'perylene': 3.94033,
                     'pyrene': 16.2806}),
    ])
    def test_other_priority_pahs(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].other_priority_pahs)

        assert self.compare_expected(samples[index].other_priority_pahs,
                                     expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2713', 0, {'c10': 3655.82,
                     'c11': 3208.21,
                     'c12': 3057.18,
                     'c13': 2850.14,
                     'c14': 840.112,
                     'c15': 2598.5,
                     'c16': 2198.84,
                     'c17': 2024.32,
                     'c18': 2092.85,
                     'c19': 1686.01,
                     'c20': 973.937,
                     'c21': 1578.58,
                     'c22': 1467.11,
                     'c23': 1405.56,
                     'c24': 1343.36,
                     'c25': 1278.89,
                     'c26': 1212.77,
                     'c27': 1152.07,
                     'c28': 1081.75,
                     'c29': 876.02,
                     'c30': 690.684,
                     'c31': 576.105,
                     'c32': 479.659,
                     'c33': 402.885,
                     'c34': 307.1,
                     'c35': 262.281,
                     'c36': 204.416,
                     'c37': 193.762,
                     'c38': 151.131,
                     'c39': 115.566,
                     'c40': 88.418,
                     'c41': 60.3058,
                     'c42': 43.0726,
                     'c43': None,
                     'c44': None,
                     'c8': None,
                     'c9': 4101.65,
                     'phytane': 882.085,
                     'pristane': 1037.14}),
        ('2713', 3, {'c10': 0.483422,
                     'c11': 3.00911,
                     'c12': 307.839,
                     'c13': 1647.96,
                     'c14': 723.36,
                     'c15': 2569.63,
                     'c16': 2574.16,
                     'c17': 2574.11,
                     'c18': 2362.87,
                     'c19': 2235.35,
                     'c20': 1441.79,
                     'c21': 2102.88,
                     'c22': 1940.93,
                     'c23': 1900.62,
                     'c24': 1777.63,
                     'c25': 1713.71,
                     'c26': 1558.06,
                     'c27': 1582.76,
                     'c28': 1494.17,
                     'c29': 1196.66,
                     'c30': 992.82,
                     'c31': 826.829,
                     'c32': 685.719,
                     'c33': 622.506,
                     'c34': 479.112,
                     'c35': 416.922,
                     'c36': 334.488,
                     'c37': 327.338,
                     'c38': 246.096,
                     'c39': 223.673,
                     'c40': 151.733,
                     'c41': 103.785,
                     'c42': 79.6474,
                     'c43': None,
                     'c44': None,
                     'c8': None,
                     'c9': 1.20045,
                     'phytane': 1105.6,
                     'pristane': 1403.92}),
    ])
    def test_n_alkanes(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].n_alkanes)

        assert self.compare_expected(samples[index].n_alkanes, expected)

    @pytest.mark.parametrize('rec, index, expected', [
        ('2234', 0, {'_14b_h_17b_h_20_cholestane': 187.856,
                     '_14b_h_17b_h_20_ethylcholestane': 240.147,
                     '_14b_h_17b_h_20_methylcholestane': 151.532,
                     '_17a_h_22_29_30_trisnorhopane': 22.3145,
                     '_18a_22_29_30_trisnorneohopane': 32.2963,
                     '_30_31_bishomohopane_22r': 82.2079,
                     '_30_31_bishomohopane_22s': 109.596,
                     '_30_31_trishomohopane_22r': 47.9958,
                     '_30_31_trishomohopane_22s': 64.9335,
                     '_30_homohopane_22r': 255.601,
                     '_30_homohopane_22s': 213.109,
                     '_30_norhopane': 27.1,
                     'c21_tricyclic_terpane': 35.3077,
                     'c22_tricyclic_terpane': 16.5779,
                     'c23_tricyclic_terpane': 106.742,
                     'c24_tricyclic_terpane': 55.274,
                     'hopane': 71.8637,
                     'pentakishomohopane_22r': 19.8337,
                     'pentakishomohopane_22s': 30.0813,
                     'tetrakishomohopane_22r': 31.9322,
                     'tetrakishomohopane_22s': 49.5613}),
        ('2234', 4, {'_14b_h_17b_h_20_cholestane': 234.598,
                     '_14b_h_17b_h_20_ethylcholestane': 304.768,
                     '_14b_h_17b_h_20_methylcholestane': 191.246,
                     '_17a_h_22_29_30_trisnorhopane': 23.6232,
                     '_18a_22_29_30_trisnorneohopane': 35.9337,
                     '_30_31_bishomohopane_22r': 105.7,
                     '_30_31_bishomohopane_22s': 141.887,
                     '_30_31_trishomohopane_22r': 60.4583,
                     '_30_31_trishomohopane_22s': 85.826,
                     '_30_homohopane_22r': 320.93,
                     '_30_homohopane_22s': 271.874,
                     '_30_norhopane': 34.5265,
                     'c21_tricyclic_terpane': 41.662,
                     'c22_tricyclic_terpane': 19.7801,
                     'c23_tricyclic_terpane': 126.434,
                     'c24_tricyclic_terpane': 65.3543,
                     'hopane': 89.1282,
                     'pentakishomohopane_22r': 22.6879,
                     'pentakishomohopane_22s': 35.8723,
                     'tetrakishomohopane_22r': 39.2143,
                     'tetrakishomohopane_22s': 60.8088}),
    ])
    def test_biomarkers(self, rec, index, expected):
        data = self.reader.get_record(rec)
        parser = EnvCanadaRecordParser(data, self.reader.file_props)

        samples = list(parser.sub_samples)
        pprint(samples[index].biomarkers)

        assert self.compare_expected(samples[index].biomarkers, expected)


class TestEnvCanadaRecordMapper(object):
    '''
        Note: still building up the new version of the mapper
    '''
    reader = EnvCanadaOilExcelFile(data_file)

    def test_init(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaRecordMapper()

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            _mapper = EnvCanadaRecordMapper(None)

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', {'_id': 'EC002713',
                  'oil_id': 'EC002713',
                  'comments': None,
                  'location': 'Alaska, USA',
                  'name': 'Alaska North Slope [2015]',
                  'product_type': 'crude',
                  'reference': {'reference': 'Hollebone, 2016. ',
                                'year': 2016},
                  'sample_date': datetime(2015, 3, 22, 0, 0),
                  }),
    ])
    def test_init_valid(self, oil_id, expected):
        '''
            We are being fairly light on the parameter checking in our
            constructor.  So if no file props are passed in, we can still
            construct the parser, but accessing reference_date could raise
            a TypeError.
            This is because the reference_date will sometimes need the
            file props if the reference field contains no date information.
        '''
        parser = EnvCanadaRecordParser(self.reader.get_record(oil_id),
                                       self.reader.file_props)
        mapper = EnvCanadaRecordMapper(parser)
        py_json = mapper.py_json()

        for k, v in expected.items():
            if v is not None:
                assert py_json[k] == v


class TestEnvCanadaSampleMapper(object):
    '''
        Note: still building up the new version of the mapper
    '''
    reader = EnvCanadaOilExcelFile(data_file)

    def test_init_invalid(self):
        with pytest.raises(TypeError):
            _mapper = EnvCanadaSampleMapper()

        with pytest.raises(TypeError):
            _mapper = EnvCanadaSampleMapper(None)

        mapper = EnvCanadaSampleMapper(None, None)

        with pytest.raises(AttributeError):
            mapper.dict()

    @pytest.mark.parametrize('oil_id, expected', [
        ('2713', {'_id': 'EC002713',
                  'oil_id': 'EC002713',
                  'comments': None,
                  'location': 'Alaska, USA',
                  'name': 'Alaska North Slope [2015]',
                  'product_type': 'crude',
                  'reference': {'reference': 'Hollebone, 2016. ',
                                'year': 2016},
                  'sample_date': datetime(2015, 3, 22, 0, 0),
                  }),
    ])
    def test_init_valid(self, oil_id, expected):
        '''
            We are being fairly light on the parameter checking in our
            constructor.  So if no file props are passed in, we can still
            construct the parser, but accessing reference_date could raise
            a TypeError.
            This is because the reference_date will sometimes need the
            file props if the reference field contains no date information.
        '''
        parser = EnvCanadaRecordParser(self.reader.get_record(oil_id),
                                       self.reader.file_props)
        mapper = EnvCanadaRecordMapper(parser)
        sub_mapper = mapper.sub_samples[0]

        assert type(sub_mapper) == EnvCanadaSampleMapper

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2713', 0, 'name', 'Fresh Oil Sample'),
        ('2713', -1, 'name', '36.76% Weathered'),
        ('540', 0, 'name', 'Fresh Oil Sample'),
        ('540', -1, 'name', '7.45% Weathered'),
        ('2713', 0, 'short_name', 'Fresh Oil'),
        ('2713', -1, 'short_name', '36.76% Weathered'),
        ('2713', 0, 'fraction_weathered', {'value': 0.0, 'unit': '1'}),
        ('2713', 0, 'boiling_point_range', None),
        ('2713', 0, 'densities', [
            {'density': {'value': 0.8751, 'unit': 'g/mL',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}},
            {'density': {'value': 0.8639, 'unit': 'g/mL',
                         'standard_deviation': 0, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}}
         ]),
        ('2713', 0, 'dynamic_viscosities', [
            {'viscosity': {'value': 17.92, 'unit': 'mPa.s',
                           'standard_deviation': 0.001, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}},
            {'viscosity': {'value': 9.852, 'unit': 'mPa.s',
                           'standard_deviation': 0.0098, 'replicates': 3},
             'ref_temp': {'unit': 'C', 'value': 15.0}}
        ]),
        ('2713', 0, 'distillation_data', [
            {'fraction': {'unit': '%', 'value': 5},
             'vapor_temp': {'unit': 'C', 'value': 60.3}},
            {'fraction': {'unit': '%', 'value': 10},
             'vapor_temp': {'unit': 'C', 'value': 91.9}},
            {'fraction': {'unit': '%', 'value': 15},
             'vapor_temp': {'unit': 'C', 'value': 119.4}},
            {'fraction': {'unit': '%', 'value': 20},
             'vapor_temp': {'unit': 'C', 'value': 147.9}},
            {'fraction': {'unit': '%', 'value': 25},
             'vapor_temp': {'unit': 'C', 'value': 180.6}},
            {'fraction': {'unit': '%', 'value': 30},
             'vapor_temp': {'unit': 'C', 'value': 215.7}},
            {'fraction': {'unit': '%', 'value': 35},
             'vapor_temp': {'unit': 'C', 'value': 247.7}},
            {'fraction': {'unit': '%', 'value': 40},
             'vapor_temp': {'unit': 'C', 'value': 277.7}},
            {'fraction': {'unit': '%', 'value': 45},
             'vapor_temp': {'unit': 'C', 'value': 308}},
            {'fraction': {'unit': '%', 'value': 50},
             'vapor_temp': {'unit': 'C', 'value': 339.1}},
            {'fraction': {'unit': '%', 'value': 55},
             'vapor_temp': {'unit': 'C', 'value': 371.2}},
            {'fraction': {'unit': '%', 'value': 60},
             'vapor_temp': {'unit': 'C', 'value': 404.3}},
            {'fraction': {'unit': '%', 'value': 65},
             'vapor_temp': {'unit': 'C', 'value': 436.3}},
            {'fraction': {'unit': '%', 'value': 70},
             'vapor_temp': {'unit': 'C', 'value': 473.3}},
            {'fraction': {'unit': '%', 'value': 75},
             'vapor_temp': {'unit': 'C', 'value': 516.4}},
            {'fraction': {'unit': '%', 'value': 80},
             'vapor_temp': {'unit': 'C', 'value': 567.6}},
            {'fraction': {'unit': '%', 'value': 85},
             'vapor_temp': {'unit': 'C', 'value': 622.6}},
            {'fraction': {'unit': '%', 'value': 90},
             'vapor_temp': {'unit': 'C', 'value': 680.2}},
            {'fraction': {'unit': '%', 'value': 0.0},
             'vapor_temp': {'unit': 'C', 'value': -11.7}},
            {'fraction': {'unit': '%', 'value': 97.5},
             'vapor_temp': {'unit': 'C', 'value': '>720'}}
        ]),
        ('2713', 0, 'pour_point', {'value': -51, 'unit': 'C',
                                   'standard_deviation': 2, 'replicates': 3}),
        ('2713', 0, 'flash_point', None),
        ('2713', 0, 'interfacial_tensions', [
            {'interface': 'air',
             'method': 'ESTS 2008',
             'tension': {'value': 27.69, 'unit': 'mN/m',
                         'standard_deviation': 0.82, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}},
            {'interface': 'water',
             'method': 'ESTS 2008',
             'tension': {'value': 24.09, 'unit': 'mN/m',
                         'standard_deviation': 0.17, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}
             },
            {'interface': 'seawater',
             'method': 'ESTS 2008',
             'tension': {'value': 22.81, 'unit': 'mN/m',
                         'standard_deviation': 0.18, 'replicates': 3},
             'ref_temp': {'value': 0.0, 'unit': 'C'}
             },
            {'interface': 'air',
             'method': 'ESTS 2008',
             'tension': {'value': 27.14, 'unit': 'mN/m',
                         'standard_deviation': 0.18, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             },
            {'interface': 'water',
             'method': 'ESTS 2008',
             'tension': {'value': 21.32, 'unit': 'mN/m',
                         'standard_deviation': 0.27, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             },
            {'interface': 'seawater',
             'method': 'ESTS 2008',
             'tension': {'value': 19.75, 'unit': 'mN/m',
                         'standard_deviation': 0.35, 'replicates': 3},
             'ref_temp': {'value': 15.0, 'unit': 'C'}
             }
         ]),
        ('2713', 0, 'dispersibilities', [
            {'dispersant': 'Corexit 9500',
             'method': 'Swirling Flask Test (ASTM F2059)',
             'effectiveness': {'value': 45.85130239898933, 'unit': '%',
                               'standard_deviation': 3.5195771460223515,
                               'replicates': 6}}
         ]),
        ('2234', 0, 'emulsions', [
            {'age': {'unit': 'day', 'value': 0},
             'method': 'ESTS 1998-2',
             'visual_stability': 'Entrained',
             'complex_modulus': {'value': 40, 'unit': 'Pa',
                                 'standard_deviation': 18, 'replicates': 6},
             'complex_viscosity': {'value': 7.097499999999999, 'unit': 'Pa.s',
                                   'standard_deviation': 2.9, 'replicates': 6},
             'loss_modulus': {'value': 40, 'unit': 'Pa',
                              'standard_deviation': 17, 'replicates': 6},
             'storage_modulus': {'value': 13.822833333333334, 'unit': 'Pa',
                                 'standard_deviation': 6, 'replicates': 6},
             'tan_delta': {'value': 3.1350000000000002, 'unit': '%',
                           'standard_deviation': 1.2, 'replicates': 6},
             'water_content': {'value': 39.78666666666666, 'unit': '%',
                               'standard_deviation': 2.3, 'replicates': 9}},
            {'age': {'unit': 'day', 'value': 7},
             'method': 'ESTS 1998-2',
             'visual_stability': None,
             'complex_modulus': {'value': 30, 'unit': 'Pa',
                                 'standard_deviation': 7, 'replicates': 6},
             'complex_viscosity': {'value': 4.979833333333333, 'unit': 'Pa.s',
                                   'standard_deviation': 1.1, 'replicates': 6},
             'loss_modulus': {'value': 30, 'unit': 'Pa',
                              'standard_deviation': 6.9, 'replicates': 6},
             'storage_modulus': {'value': 2.4436666666666667, 'unit': 'Pa',
                                 'standard_deviation': 0.96, 'replicates': 6},
             'tan_delta': {'value': 13.883333333333333, 'unit': '%',
                           'standard_deviation': 4.1, 'replicates': 6},
             'water_content': {'value': 15.592222222222224, 'unit': '%',
                               'standard_deviation': 1.8, 'replicates': 9}}
         ]),
        ('2713', 0, 'sara', {
            'method': 'ESTS 2014',
            'aromatics': {'value': 31.9, 'unit': '%',
                          'standard_deviation': 0.21575863999286224,
                          'replicates': 3},
            'asphaltenes': {'value': 3.979387689417676, 'unit': '%',
                            'standard_deviation': 0.13573969703208513,
                            'replicates': 3},
            'resins': {'value': 6.450610574167082, 'unit': '%',
                       'standard_deviation': 0.21575863999286224,
                       'replicates': 3},
            'saturates': {'value': 57.9, 'unit': '%',
                          'standard_deviation': 0.21575863999286224,
                          'replicates': 3}
         }),
    ])
    def test_attribute(self, oil_id, index, attr, expected):
        parser = EnvCanadaRecordParser(self.reader.get_record(oil_id),
                                       self.reader.file_props)
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        pprint(getattr(sub_mapper, attr))
        assert getattr(sub_mapper, attr) == expected

    @pytest.mark.parametrize('oil_id, index, attr, expected', [
        ('2234', 0, 'compounds', {
            'list_size': 91,
            'total_groups': {
                'Alkylated Total Aromatic Hydrocarbons (PAHs) (µg/g oil) '
                '(ESTS 2002a):',
                'Biomarkers (µg/g) (ESTS 2002a):',
                'n-Alkanes (µg/g oil) (ESTS 2002a):',
            }
         }),
        ('561', 0, 'compounds', {
            'list_size': 114,
            'total_groups': {
                'Alkylated Total Aromatic Hydrocarbons (PAHs) (µg/g oil) '
                '(ESTS 2002a):',
                'C4-C6 Alkyl Benzenes (µg/g) (ESTS 2002b):',
                'Biomarkers (µg/g) (ESTS 2002a):',
                'BTEX group (µg/g) (ESTS 2002b)',
                'n-Alkanes (µg/g oil) (ESTS 2002a):',
                'Benzene and Alkynated Benzene (ESTS 2002b)'
            }
         }),
    ])
    def test_compound_list(self, oil_id, index, attr, expected):
        parser = EnvCanadaRecordParser(self.reader.get_record(oil_id),
                                       self.reader.file_props)
        sub_mapper = EnvCanadaRecordMapper(parser).sub_samples[index]

        compounds = getattr(sub_mapper, attr)

        # We won't be checking every single compound since there are typically
        # over one hundred to check.  We will verify general properties of our
        # compound list though
        assert type(compounds) == list
        assert len(compounds) == expected['list_size']

        for c in compounds:
            for attr in ('name', 'method', 'groups', 'measurement'):
                assert attr in c

            for attr in ('value', 'unit', 'unit_type'):
                assert attr in c['measurement']

        total_groups = set([sub for c in compounds for sub in c['groups']])
        print(total_groups)

        assert total_groups == expected['total_groups']
















