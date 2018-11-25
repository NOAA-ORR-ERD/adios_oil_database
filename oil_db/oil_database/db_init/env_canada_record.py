#
# This is where we handle the initialization of oil record objects that come
# from the Environment Canada oil properties spreadsheet.
#
import sys
import logging

import numpy as np

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from ..util.term import TermColor as tc

from ..data_sources.env_canada.oil_library import (EnvCanadaOilExcelFile,
                                                   EnvCanadaRecordParser)

from ..models.ec_imported_rec import ECImportedRecord

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def add_ec_records(settings):
    '''
        Add the records from the Environment Canada Excel spreadsheet
        of oil properties.
    '''
    for fn in settings['oillib.ec_files'].split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = EnvCanadaOilExcelFile(fn)

        print('Adding new records to database')

        rowcount = 0
        for rec in fd.get_records():
            try:
                add_ec_record(fd.field_indexes, rec)
            except ValidationError as e:
                parser = EnvCanadaRecordParser(fd.field_indexes, rec)
                rec_id = tc.change(parser.ec_oil_id, 'red')

                print ('validation failed for {}: {}'.format(rec_id, e))
            except DuplicateKeyError as e:
                parser = EnvCanadaRecordParser(fd.field_indexes, rec)
                rec_id = tc.change(parser.ec_oil_id, 'red')

                print ('duplicate fields for {}: {}'.format(rec_id, e))

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print('finished!!!  {0} rows processed.'.format(rowcount))


def add_ec_record(field_indexes, values):
    '''
        Add an Environment Canada Record
    '''
    parser = EnvCanadaRecordParser(field_indexes, values)
    name = parser.name

    # For now, we will debug only certain records.
    # TODO: we need to turn this into a suite of pytests
    if name == 'Alaminos Canyon Block 25':
        test_oil_record(parser)
    elif name == 'Access West Winter Blend':
        test_access_west(parser)
    elif name == 'Cook Inlet [2003]':
        test_cook_inlet(parser)

    model_rec = ECImportedRecord.from_record_parser(parser)
    model_rec.save()


def test_oil_record(parser):
    '''
        Test an Environment Canada Record ('Alaminos Canyon Block 25')
    '''
    print
    print '--- Testing Oil Record ---'
    print 'name: {}'.format(parser.name)
    print 'ESTS codes: {}'.format(parser.ests_codes)
    print 'weathered: {}'.format(parser.weathering)
    print 'reference: {}'.format(parser.reference)
    print 'reference date: {}'.format(parser.reference_date)
    print 'comments: {}'.format(parser.comments)
    print 'EC Oil ID: {}'.format(parser.ec_oil_id)
    print 'location: {}'.format(parser.location)

    print 'oil API: {}'.format(parser.api)

    print 'densities:'
    pp.pprint(parser.densities)

    assert np.allclose([d['kg_m_3'] for d in parser.densities],
                       [892.1, 912.65, 941.667, 871.367,
                        885.867, 897.9, 932.0],
                       rtol=0.0001)
    for label in ('density_0_c_g_ml',
                  'density_5_c_g_ml',
                  'density_15_c_g_ml'):
        assert all([label not in v
                    for v in parser.viscosities])

    print 'viscosities:'
    pp.pprint(parser.viscosities)

    assert np.allclose([v['kg_ms'] for v in parser.viscosities],
                       [0.0552867, 0.1799333, 0.6034667, 2.77,
                        0.03, 0.07509, 0.2057, 0.6874],
                       rtol=0.0001)
    assert all([m1 == m2
                for m1, m2
                in zip([t['method'] for t in parser.viscosities],
                       ['ESTS 2003'] * 8)])

    for label in ('viscosity_at_0_c_mpa_s',
                  'viscosity_at_5_c_mpa_s',
                  'viscosity_at_15_c_mpa_s'):
        assert all([label not in v
                    for v in parser.viscosities])

    print 'interfacial tensions:'
    pp.pprint(parser.interfacial_tensions)

    assert np.allclose([t['n_m'] for t in parser.interfacial_tensions],
                       [0.028255, 0.025587, 0.024750, 0.028987,
                        0.026423, 0.026486, 0.030956, 0.024932,
                        0.023723, 0.032463, 0.027856, 0.023025,
                        0.024601, 0.028464, 0.022822, 0.024526,
                        0.030238, 0.026356, 0.023258, 0.030915,
                        0.024770, 0.019876],
                       rtol=0.0001)

    assert all([m1 == m2
                for m1, m2
                in zip([t['method'] for t in parser.interfacial_tensions],
                       ['ASTM D971 mod.'] * 22)])

    for label in ('surface_tension_15_c_oil_air',
                  'interfacial_tension_15_c_oil_water',
                  'interfacial_tension_15_c_oil_salt_water_3_3_nacl'):
        assert all([label not in v
                    for v in parser.viscosities])

    print 'flash points:'
    pp.pprint(parser.flash_points)

    assert np.allclose([(f['min_temp_k'],
                         np.nan if f['max_temp_k'] is None else f['max_temp_k'])
                        for f in parser.flash_points],
                       [(273.15, np.nan),
                        (308.65, 308.65),
                        (348.15, 348.15),
                        (391.15, 391.15)],
                       rtol=0.0001, equal_nan=True)

    for label in ('flash_point',):
        assert all([label not in v
                    for v in parser.viscosities])

    print 'pour points:'
    pp.pprint(parser.pour_points)

    assert np.allclose([(p['min_temp_k'], p['max_temp_k'])
                        for p in parser.pour_points],
                       [(201.15, 201.15),
                        (222.65, 222.65),
                        (233.15, 233.15),
                        (238.15, 238.15)],
                       rtol=0.0001)

    for label in ('pour_point',):
        assert all([label not in v
                    for v in parser.viscosities])

    print 'distillation cuts:'
    pp.pprint(parser.distillation_cuts)

    assert np.allclose([c['fraction'] for c in parser.distillation_cuts],
                       [2.32, 2.97, 5.44, 7.14, 9.04, 11.24, 13.84, 16.54, 18.94, 25.64,
                        33.14, 41.14, 48.94, 57.24, 64.34, 70.44, 75.54, 80.04,
                        0L, 0L, 0.78, 1.68, 3.08, 4.98, 7.48, 10.18, 12.68, 19.88,
                        27.88, 36.28, 44.58, 53.38, 61.08, 67.88, 73.58, 78.58,
                        0L, 0L, 0L, 0.1, 0.2, 0.7, 2.1, 4.4, 7L, 14.8,
                        23.7, 33.1, 42.4, 52.3, 60.9, 68.3, 74.4, 79.7,
                        0L, 0L, 0L, 0L, 0L, 0L, 0L, 0.1, 0.7, 6.8,
                        16.4, 26.9, 37.3, 48.4, 58.2, 66.5, 73.4, 79.3],
                       rtol=0.0001)

    print 'adhesions:'
    pp.pprint(parser.adhesions)

    assert np.allclose([a['kg_m_2'] for a in parser.adhesions],
                       [400L, 300L, 249.205, 400L],
                       rtol=0.0001)

    for label in ('adhesion',):
        assert all([label not in v
                    for v in parser.adhesions])

    print 'evaporation eqs:'
    pp.pprint(parser.evaporation_eqs)

    assert np.allclose((parser.evaporation_eqs[0]['a'],
                        parser.evaporation_eqs[0]['b']),
                       (2.01, 0.045),
                       rtol=0.0001)

    print 'emulsions:'
    pp.pprint(parser.emulsions)
    # no data to test here for this record.

    print 'corexit:'
    pp.pprint(parser.corexit)
    # no data to test here for this record.

    print 'sulfur content:'
    pp.pprint(parser.sulfur_content)

    assert np.allclose([c['fraction'] for c in parser.sulfur_content],
                       [0.009081, 0.012306, 0.013447, 0.014945],
                       rtol=0.0001)

    print 'water content:'
    pp.pprint(parser.water_content)

    assert np.allclose([c['fraction'] for c in parser.water_content],
                       [0.002, 0.001, 0.001, 0.001],
                       rtol=0.0001)

    print 'wax content:'
    pp.pprint(parser.wax_content)
    assert np.allclose([c['fraction'] for c in parser.wax_content],
                       [0.00504, 0.00641, 0.00594, 0.00533],
                       rtol=0.0001)

    print 'benzene content:'
    pp.pprint(parser.benzene_content)

    assert np.allclose([c['benzene_ppm'] for c in parser.benzene_content],
                       [130L, 50L, 10L, 0L],
                       rtol=0.0001)

    assert np.allclose([c['toluene_ppm'] for c in parser.benzene_content],
                       [1170L, 830L, 40L, 0L],
                       rtol=0.0001)

    assert np.allclose([c['ethylbenzene_ppm'] for c in parser.benzene_content],
                       [510L, 460L, 130L, 0L],
                       rtol=0.0001)

    print 'headspace:'
    pp.pprint(parser.headspace)
    # no data to test here for this record.

    print 'CCME Fractions:'
    pp.pprint(parser.ccme)
    # no data to test here for this record.

    print 'CCME F1 Saturates:'
    pp.pprint(parser.ccme_f1)
    # no data to test here for this record.

    print 'CCME F2 Aromatics:'
    pp.pprint(parser.ccme_f2)
    # no data to test here for this record.

    print 'CCME GC-TPH:'
    pp.pprint(parser.ccme_tph)
    # no data to test here for this record.

    print 'n-Alkanes:'
    pp.pprint(parser.alkanes)

    assert np.allclose([a['pristane_ug_g'] for a in parser.alkanes],
                       [1080L, 1120L, 1410L, 1330L])

    assert np.allclose([a['phytane_ug_g'] for a in parser.alkanes],
                       [920L, 1020L, 1170L, 1180L])

    assert np.allclose([a['c8_ug_g'] for a in parser.alkanes],
                       [3940L, 3160L, 380L, 360L])

    assert np.allclose([a['c9_ug_g'] for a in parser.alkanes],
                       [2980L, 2910L, 1430L, 1430L])

    assert np.allclose([a['c10_ug_g'] for a in parser.alkanes],
                       [2220L, 2220L, 1910L, 1890L])

    assert np.allclose([a['c11_ug_g'] for a in parser.alkanes],
                       [2050L, 2170L, 2260L, 2200L])

    assert np.allclose([a['c12_ug_g'] for a in parser.alkanes],
                       [1630L, 1910L, 2060L, 1980L])

    assert np.allclose([a['c13_ug_g'] for a in parser.alkanes],
                       [1280L, 1580L, 1610L, 1770L])

    assert np.allclose([a['c14_ug_g'] for a in parser.alkanes],
                       [1110L, 1110L, 1240L, 1200L])

    assert np.allclose([a['c15_ug_g'] for a in parser.alkanes],
                       [720L, 820L, 930L, 900L])

    assert np.allclose([a['c16_ug_g'] for a in parser.alkanes],
                       [420L, 480L, 520L, 480L])

    assert np.allclose([a['c17_ug_g'] for a in parser.alkanes],
                       [290L, 280L, 390L, 340L])

    assert np.allclose([a['c18_ug_g'] for a in parser.alkanes],
                       [370L, 380L, 490L, 450L])

    assert np.allclose([a['c19_ug_g'] for a in parser.alkanes],
                       [180L, 190L, 190L, 220L])

    assert np.allclose([a['c20_ug_g'] for a in parser.alkanes],
                       [320L, 350L, 400L, 430L])

    assert np.allclose([a['c21_ug_g'] for a in parser.alkanes],
                       [260L, 300L, 310L, 340L])

    assert np.allclose([a['c22_ug_g'] for a in parser.alkanes],
                       [250L, 290L, 300L, 310L])

    assert np.allclose([a['c23_ug_g'] for a in parser.alkanes],
                       [230L, 250L, 290L, 310L])

    assert np.allclose([a['c24_ug_g'] for a in parser.alkanes],
                       [280L, 230L, 300L, 320L])

    assert np.allclose([a['c25_ug_g'] for a in parser.alkanes],
                       [280L, 320L, 320L, 330L])

    assert np.allclose([a['c26_ug_g'] for a in parser.alkanes],
                       [260L, 270L, 290L, 320L])

    assert np.allclose([a['c27_ug_g'] for a in parser.alkanes],
                       [220L, 240L, 290L, 280L])

    assert np.allclose([a['c28_ug_g'] for a in parser.alkanes],
                       [150L, 190L, 290L, 140L])

    assert np.allclose([a['c29_ug_g'] for a in parser.alkanes],
                       [170L, 180L, 230L, 220L])

    assert np.allclose([a['c30_ug_g'] for a in parser.alkanes],
                       [170L, 190L, 270L, 240L])

    assert np.allclose([a['c31_ug_g'] for a in parser.alkanes],
                       [140L, 170L, 190L, 190L])

    assert np.allclose([a['c32_ug_g'] for a in parser.alkanes],
                       [120L, 120L, 140L, 130L])

    assert np.allclose([a['c33_ug_g'] for a in parser.alkanes],
                       [90L, 90L, 120L, 130L])

    assert np.allclose([a['c34_ug_g'] for a in parser.alkanes],
                       [80L, 80L, 110L, 120L])

    assert np.allclose([a['c35_ug_g'] for a in parser.alkanes],
                       [70L, 90L, 110L, 110L])

    assert np.allclose([a['c36_ug_g'] for a in parser.alkanes],
                       [40L, 50L, 60L, 70L])

    assert np.allclose([a['c37_ug_g'] for a in parser.alkanes],
                       [30L, 40L, 40L, 40L])

    assert np.allclose([a['c38_ug_g'] for a in parser.alkanes],
                       [30L, 30L, 40L, 50L])

    assert np.allclose([np.nan if a['c39_ug_g'] is None else a['c39_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, 30L, 40L],
                       equal_nan=True)

    assert np.allclose([np.nan if a['c40_ug_g'] is None else a['c40_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, np.nan, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if a['c41_ug_g'] is None else a['c41_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, np.nan, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if a['c42_ug_g'] is None else a['c42_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, np.nan, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if a['c43_ug_g'] is None else a['c43_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, np.nan, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if a['c44_ug_g'] is None else a['c44_ug_g']
                        for a in parser.alkanes],
                       [np.nan, np.nan, np.nan, np.nan],
                       equal_nan=True)

    print 'biomarkers:'
    pp.pprint(parser.biomarkers)

    assert np.allclose([b['_14ss_h_17ss_h_20_cholestane_c27assss_ppm']
                        for b in parser.biomarkers],
                       [100L, 116L, 123L, 125L])

    assert np.allclose([b['_14ss_h_17ss_h_20_ethylcholestane_c29assss_ppm']
                        for b in parser.biomarkers],
                       [116L, 134L, 139L, 151L])

    assert np.allclose([b['_14ss_h_17ss_h_20_methylcholestane_c28assss_ppm']
                        for b in parser.biomarkers],
                       [127L, 144L, 159L, 172L])

    assert np.allclose([b['_17a_h_22_29_30_trisnorhopane_c27tm_ppm']
                        for b in parser.biomarkers],
                       [36.6, 43.2, 46.1, 47.4])

    assert np.allclose([b['_18a_22_29_30_trisnorneohopane_c27ts_ppm']
                        for b in parser.biomarkers],
                       [28.2, 33.8, 35.9, 36L])

    assert np.allclose([b['_30_31_bishomohopane_22r_h32r_ppm']
                        for b in parser.biomarkers],
                       [21.3, 24.3, 26L, 27.3])

    assert np.allclose([b['_30_31_bishomohopane_22s_h32s_ppm']
                        for b in parser.biomarkers],
                       [27L, 30.6, 32.8, 33.8])

    assert np.allclose([b['_30_31_trishomohopane_22r_h33r_ppm']
                        for b in parser.biomarkers],
                       [12.1, 13.5, 14.2, 15.1])

    assert np.allclose([b['_30_31_trishomohopane_22s_h33s_ppm']
                        for b in parser.biomarkers],
                       [18.6, 22.2, 23.5, 24.8])

    assert np.allclose([b['_30_homohopane_22r_h31r_ppm']
                        for b in parser.biomarkers],
                       [37.6, 43.5, 45.4, 48.7])

    assert np.allclose([b['_30_homohopane_22s_h31s_ppm']
                        for b in parser.biomarkers],
                       [45.6, 52.5, 58.7, 64L])

    assert np.allclose([b['_30_norhopane_h29_ppm']
                        for b in parser.biomarkers],
                       [94.9, 113L, 118L, 143L])

    assert np.allclose([b['c21_tricyclic_terpane_c21t_ppm']
                        for b in parser.biomarkers],
                       [8.1, 10.2, 10.7, 11.6])

    assert np.allclose([b['c22_tricyclic_terpane_c22t_ppm']
                        for b in parser.biomarkers],
                       [3.93, 4.41, 4.35, 5.2])

    assert np.allclose([b['c23_tricyclic_terpane_c23t_ppm']
                        for b in parser.biomarkers],
                       [15.4, 17.1, 20.3, 20.5])

    assert np.allclose([b['c24_tricyclic_terpane_c24t_ppm']
                        for b in parser.biomarkers],
                       [10.8, 12.2, 12.4, 12.9])

    assert np.allclose([b['hopane_h30_ppm']
                        for b in parser.biomarkers],
                       [132L, 147L, 161L, 162L])

    assert np.allclose([b['pentakishomohopane_22r_h35r_ppm']
                        for b in parser.biomarkers],
                       [8.12, 8.53, 9.39, 9.58])

    assert np.allclose([b['pentakishomohopane_22s_h35s_ppm']
                        for b in parser.biomarkers],
                       [7.26, 8.58, 9.63, 9.13])

    assert np.allclose([b['tetrakishomohopane_22r_h34r_ppm']
                        for b in parser.biomarkers],
                       [6.87, 8.45, 8.5, 8.63])

    assert np.allclose([b['tetrakishomohopane_22s_h34s_ppm']
                        for b in parser.biomarkers],
                       [14.2, 16.7, 17.6, 18.8])

    print 'sara total fractions:'
    pp.pprint(parser.sara_total_fractions)

    assert np.allclose([f['fraction']
                        for f in parser.sara_total_fractions
                        if f['sara_type'] == 'Saturates'],
                       [0.7901, 0.7845, 0.7704, 0.7412],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in parser.sara_total_fractions
                        if f['sara_type'] == 'Aromatics'],
                       [0.13160, 0.13261, 0.134498, 0.134399],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in parser.sara_total_fractions
                        if f['sara_type'] == 'Resins'],
                       [0.071415, 0.076691, 0.088457, 0.11271],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in parser.sara_total_fractions
                        if f['sara_type'] == 'Asphaltenes'],
                       [0.0068768, 0.0061916, 0.0066182, 0.011667],
                       rtol=0.0001)

    # Note: This will fail because the Hydrocarbon Group Content block in the
    #       spreadsheet contains two Method fields.  So this value gets
    #       clobbered.  It would be nice to find a good way to fix this
    #       without creating an exceptional case in the category function.
    # assert all([m1 == m2
    #             for m1, m2
    #             in zip([t['method'] for t in rec.sara_total_fractions],
    #                    ['ESTS 2003'] * 16)])

    print


def test_access_west(parser):
    '''
        Test an Environment Canada Record ('Access West Winter Blend')

        We added testing for this record specifically to cover content that
        the Alaminos record is missing.
    '''
    print
    print 'name: {}'.format(parser.name)
    print 'weathered: {}'.format(parser.weathering)
    print 'reference: {}'.format(parser.reference)

    print 'emulsions:'
    pp.pprint(parser.emulsions)

    assert np.allclose([d['water_content_fraction'] for d in parser.emulsions],
                       [0.397867, 0.350256, 0.3, 0.0640556,
                        0.1559222, 0.2417778, 0.2997333, 0.0601167],
                       rtol=0.0001)

    assert np.allclose([d['age_days'] for d in parser.emulsions],
                       [0.0, 0.0, 0.0, 0.0, 7.0, 7.0, 7.0, 7.0],
                       rtol=0.0001)

    assert np.allclose([d['ref_temp_k'] for d in parser.emulsions],
                       [288.15] * 8,
                       rtol=0.0001)

    print 'corexit:'
    pp.pprint(parser.corexit)

    assert np.allclose([d['dispersant_effectiveness_fraction']
                        for d in parser.corexit],
                       [0.103994, 0.1])

    assert np.allclose([d['replicates']
                        for d in parser.corexit],
                       [6L, 6L])

    assert np.allclose([d['standard_deviation']
                        for d in parser.corexit],
                       [1.8703, 1.2511])

    for label in ('water_content_w_w',):
        assert all([label not in v
                    for v in parser.emulsions])

    print 'CCME Fractions:'
    pp.pprint(parser.ccme)

    assert np.allclose([c['ccme_f1_mg_g'] for c in parser.ccme],
                       [15.5836, 15.5019, 15.3019, 1.62313, 1.59845])

    assert np.allclose([c['ccme_f2_mg_g'] for c in parser.ccme],
                       [50.0558, 53.2612, 60.108, 28.1604, 14.829])

    assert np.allclose([c['ccme_f3_mg_g'] for c in parser.ccme],
                       [193.131, 207.703, 248.135, 251.512, 248.196])

    assert np.allclose([c['ccme_f4_mg_g'] for c in parser.ccme],
                       [40.2255, 40.8225, 32.7845, 31.4471, 36.232])

    print 'CCME F1 Saturates:'
    pp.pprint(parser.ccme_f1)

    assert np.allclose([c['n_c8_to_n_c10'] for c in parser.ccme_f1],
                       [18.35, 17.54, 15.98, 1.89, 1.73])

    assert np.allclose([c['n_c10_to_n_c12'] for c in parser.ccme_f1],
                       [10.82, 11.15, 12.19, 0.69, 0.5])

    assert np.allclose([c['n_c12_to_n_c16'] for c in parser.ccme_f1],
                       [29.75, 30.97, 35.75, 18.08, 7.93])

    assert np.allclose([c['n_c16_to_n_c20'] for c in parser.ccme_f1],
                       [30.84, 32.12, 37.47, 37.54, 34.77])

    assert np.allclose([c['n_c20_to_n_c24'] for c in parser.ccme_f1],
                       [21.56, 22.89, 26.19, 28.3, 29.69])

    assert np.allclose([c['n_c24_to_n_c28'] for c in parser.ccme_f1],
                       [16.03, 17.29, 19.77, 22.05, 23L])

    assert np.allclose([c['n_c28_to_n_c34'] for c in parser.ccme_f1],
                       [22.23, 24.1, 28.29, 32.11, 33.36])

    assert np.allclose([c['n_c34'] for c in parser.ccme_f1],
                       [14.79, 17.36, 14.05, 16.9, 18.57])

    print 'CCME F2 Aromatics:'
    pp.pprint(parser.ccme_f2)

    assert np.allclose([c['n_c8_to_n_c10'] for c in parser.ccme_f2],
                       [3.72, 3.9, 5.04, 1.51, 1.27])

    assert np.allclose([c['n_c10_to_n_c12'] for c in parser.ccme_f2],
                       [2.17, 2.52, 3.05, 0.95, 0.71])

    assert np.allclose([c['n_c12_to_n_c16'] for c in parser.ccme_f2],
                       [5.56, 6.42, 6.9, 5.21, 2.9])

    assert np.allclose([c['n_c16_to_n_c20'] for c in parser.ccme_f2],
                       [17.05, 18.88, 22.19, 20.95, 19.06])

    assert np.allclose([c['n_c20_to_n_c24'] for c in parser.ccme_f2],
                       [23.43, 26.01, 30.57, 29.7, 29.61])

    assert np.allclose([c['n_c24_to_n_c28'] for c in parser.ccme_f2],
                       [23.11, 25.9, 30.79, 30.45, 30.68])

    assert np.allclose([c['n_c28_to_n_c34'] for c in parser.ccme_f2],
                       [33L, 36.71, 43.91, 42.48, 42.32])

    assert np.allclose([c['n_c34'] for c in parser.ccme_f2],
                       [26.59, 23.52, 24.19, 23.92, 24.75])

    print 'CCME GC-TPH:'
    pp.pprint(parser.ccme_tph)

    assert np.allclose([c['n_c8_to_n_c10'] for c in parser.ccme_tph],
                       [15.24, 15.77, 14.66, 2.5, 1.88])

    assert np.allclose([c['n_c10_to_n_c12'] for c in parser.ccme_tph],
                       [14.17, 14.93, 15.96, 1.97, 1.11])

    assert np.allclose([c['n_c12_to_n_c16'] for c in parser.ccme_tph],
                       [37.59, 40.35, 46.13, 25.23, 11.35])

    assert np.allclose([c['n_c16_to_n_c20'] for c in parser.ccme_tph],
                       [48.43, 52.68, 60.89, 59.07, 54.53])

    assert np.allclose([c['n_c20_to_n_c24'] for c in parser.ccme_tph],
                       [45.4, 50.12, 57.96, 58.62, 60.92])

    assert np.allclose([c['n_c24_to_n_c28'] for c in parser.ccme_tph],
                       [40.4, 44.24, 52.64, 54.19, 55.03])

    assert np.allclose([c['n_c28_to_n_c34'] for c in parser.ccme_tph],
                       [58.12, 63.67, 73.49, 75.22, 73.02])

    assert np.allclose([c['n_c34'] for c in parser.ccme_tph],
                       [39.67, 35.52, 34.61, 35.95, 43.01])

    assert np.allclose([c['total_tph_gc_detected_tph_undetected_tph']
                        for c in parser.ccme_tph],
                       [690L, 680L, 640L, 540L, 460L])


def test_cook_inlet(parser):
    '''
        Test an Environment Canada Record ('Cook Inlet [2003]')

        We added testing for this record specifically because neither the
        Alaminos nor the Access West record has headspace information.
    '''
    print
    print 'name: {}'.format(parser.name)
    print 'weathered: {}'.format(parser.weathering)
    print 'reference: {}'.format(parser.reference)

    print 'headspace:'
    pp.pprint(parser.headspace)

    assert np.allclose([np.nan if h['n_c5_mg_g'] is None else h['n_c5_mg_g']
                        for h in parser.headspace],
                       [16.689, 2.59228, 0L, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if h['n_c6_mg_g'] is None else h['n_c6_mg_g']
                        for h in parser.headspace],
                       [9.19397, 6.52227, 0L, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if h['n_c7_mg_g'] is None else h['n_c7_mg_g']
                        for h in parser.headspace],
                       [5.0631, 0.159752, 0L, np.nan],
                       equal_nan=True)

    assert np.allclose([np.nan if h['n_c8_mg_g'] is None else h['n_c8_mg_g']
                        for h in parser.headspace],
                       [5.43, 4.946, 0.266, 0L],
                       equal_nan=True)

    assert np.allclose([(np.nan if h['c5_group_mg_g'] is None
                         else h['c5_group_mg_g'])
                        for h in parser.headspace],
                       [49.414, 1.692977, 0L, np.nan],
                       equal_nan=True)

    assert np.allclose([(np.nan if h['c6_group_mg_g'] is None
                         else h['c6_group_mg_g'])
                        for h in parser.headspace],
                       [54.82347, 29.7478, 0L, np.nan],
                       equal_nan=True)

    assert np.allclose([(np.nan if h['c7_group_mg_g'] is None
                         else h['c7_group_mg_g'])
                        for h in parser.headspace],
                       [29.2017, 26.65767, 0L, np.nan],
                       equal_nan=True)
