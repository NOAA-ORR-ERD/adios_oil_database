#
# This is where we handle the initialization of oil record objects that come
# from the Exxon assay spreadsheets.
#
import sys
import logging

import numpy as np

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from ..util.term import TermColor as tc

from ..util.csv import CSVFileWithHeader
from ..data_sources.exxon_assays.oil_library import (ExxonOilExcelFile,
                                                     ExxonRecordParser)

from ..models.ec_imported_rec import ECImportedRecord

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def add_exxon_records(settings):
    '''
        Add the records from the Exxon assay Excel spreadsheets
        of oil properties.
    '''
    for name, filename in get_exxon_assay_files(settings):
        logger.info('\topening assay file: {0} ...'.format(filename))
        # fd = ExxonOilExcelFile(fn)

        # print ('Adding new records to database')

#         rowcount = 0
#         for rec in fd.get_records():
#             try:
#                 add_ec_record(fd.field_indexes, rec)
#             except ValidationError as e:
#                 parser = ExxonRecordParser(fd.field_indexes, rec)
#                 rec_id = tc.change(parser.ec_oil_id, 'red')
#    
#                 print ('validation failed for {}: {}'.format(rec_id, e))
#             except DuplicateKeyError as e:
#                 parser = ExxonRecordParser(fd.field_indexes, rec)
#                 rec_id = tc.change(parser.ec_oil_id, 'red')
#    
#                 print ('duplicate fields for {}: {}'.format(rec_id, e))
#    
#             if rowcount % 100 == 0:
#                 sys.stderr.write('.')
#  
#             rowcount += 1
#
#        print ('finished!!!  {0} rows processed.'.format(rowcount))


def get_exxon_assay_files(settings):
    '''
        Our settings contain a list of index files in .csv format.
        Each row in our files contains an oil_name and its associated
        assay_file.
    '''
    for fn in settings['oillib.exxon_files'].split('\n'):
        logger.info('opening index file: {0} ...'.format(fn))
        with CSVFileWithHeader(fn) as csv_file:
            for name, filename in csv_file.readlines():
                yield name, filename


def add_ec_record(field_indexes, values):
    '''
        Add an Environment Canada Record
    '''
    parser = ExxonRecordParser(field_indexes, values)
    name = parser.name

    # For now, we will debug only certain records.
    # TODO: we need to turn this into a suite of pytests
    if name == 'Alaminos Canyon Block 25':
        print u'testing {}: "{}"'.format(name, parser.ec_oil_id)
        test_alaminos(parser)
    elif name == 'Access West Winter Blend':
        print u'testing {}: "{}"'.format(name, parser.ec_oil_id)
        test_access_west(parser)

    model_rec = ECImportedRecord.from_record_parser(parser)
    model_rec.save()


def test_alaminos(rec):
    '''
        Test an Environment Canada Record ('Alaminos Canyon Block 25')
    '''
    print
    print 'name: {}'.format(rec.name)
    print 'ESTS codes: {}'.format(rec.ests_codes)
    print 'weathered: {}'.format(rec.weathering)
    print 'reference: {}'.format(rec.reference)
    print 'reference date: {}'.format(rec.reference_date)
    print 'comments: {}'.format(rec.comments)
    print 'EC Oil ID: {}'.format(rec.ec_oil_id)
    print 'location: {}'.format(rec.location)

    print 'oil API: {}'.format(rec.api)

    print 'densities:'
    pp.pprint(rec.densities)

    assert np.allclose([d['kg_m_3'] for d in rec.densities],
                       [892.1, 912.65, 941.667, 871.367,
                        885.867, 897.9, 932.0],
                       rtol=0.0001)
    for label in ('density_0_c_g_ml',
                  'density_5_c_g_ml',
                  'density_15_c_g_ml'):
        assert all([label not in v
                    for v in rec.viscosities])

    print 'viscosities:'
    pp.pprint(rec.viscosities)

    assert np.allclose([v['kg_ms'] for v in rec.viscosities],
                       [0.0552867, 0.1799333, 0.6034667, 2.77,
                        0.03, 0.07509, 0.2057, 0.6874],
                       rtol=0.0001)
    assert all([m1 == m2
                for m1, m2
                in zip([t['method'] for t in rec.viscosities],
                       ['ESTS 2003'] * 8)])

    for label in ('viscosity_at_0_c_mpa_s',
                  'viscosity_at_5_c_mpa_s',
                  'viscosity_at_15_c_mpa_s'):
        assert all([label not in v
                    for v in rec.viscosities])

    print 'interfacial tensions:'
    pp.pprint(rec.interfacial_tensions)

    assert np.allclose([t['n_m'] for t in rec.interfacial_tensions],
                       [0.028255, 0.025587, 0.024750, 0.028987,
                        0.026423, 0.026486, 0.030956, 0.024932,
                        0.023723, 0.032463, 0.027856, 0.023025,
                        0.024601, 0.028464, 0.022822, 0.024526,
                        0.030238, 0.026356, 0.023258, 0.030915,
                        0.024770, 0.019876],
                       rtol=0.0001)

    assert all([m1 == m2
                for m1, m2
                in zip([t['method'] for t in rec.interfacial_tensions],
                       ['ASTM D971 mod.'] * 22)])

    for label in ('surface_tension_15_c_oil_air',
                  'interfacial_tension_15_c_oil_water',
                  'interfacial_tension_15_c_oil_salt_water_3_3_nacl'):
        assert all([label not in v
                    for v in rec.viscosities])

    print 'flash points:'
    pp.pprint(rec.flash_points)

    assert np.allclose([(f['min_temp_k'],
                         np.nan if f['max_temp_k'] is None else f['max_temp_k'])
                        for f in rec.flash_points],
                       [(273.15, np.nan),
                        (308.65, 308.65),
                        (348.15, 348.15),
                        (391.15, 391.15)],
                       rtol=0.0001, equal_nan=True)

    for label in ('flash_point',):
        assert all([label not in v
                    for v in rec.viscosities])

    print 'pour points:'
    pp.pprint(rec.pour_points)

    assert np.allclose([(p['min_temp_k'], p['max_temp_k'])
                        for p in rec.pour_points],
                       [(201.15, 201.15),
                        (222.65, 222.65),
                        (233.15, 233.15),
                        (238.15, 238.15)],
                       rtol=0.0001)

    for label in ('pour_point',):
        assert all([label not in v
                    for v in rec.viscosities])

    print 'distillation cuts:'
    pp.pprint(rec.distillation_cuts)

    assert np.allclose([c['fraction'] for c in rec.distillation_cuts],
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
    pp.pprint(rec.adhesions)

    assert np.allclose([a['kg_m_2'] for a in rec.adhesions],
                       [400L, 300L, 249.205, 400L],
                       rtol=0.0001)

    for label in ('adhesion',):
        assert all([label not in v
                    for v in rec.adhesions])

    print 'evaporation eqs:'
    pp.pprint(rec.evaporation_eqs)

    assert np.allclose((rec.evaporation_eqs[0]['a'],
                        rec.evaporation_eqs[0]['b']),
                       (2.01, 0.045),
                       rtol=0.0001)

    print 'emulsions:'
    pp.pprint(rec.emulsions)
    # no data to test here for this record.

    print 'sulfur content:'
    pp.pprint(rec.sulfur_content)

    assert np.allclose([c['fraction'] for c in rec.sulfur_content],
                       [0.009081, 0.012306, 0.013447, 0.014945],
                       rtol=0.0001)

    print 'water content:'
    pp.pprint(rec.water_content)

    assert np.allclose([c['fraction'] for c in rec.water_content],
                       [0.002, 0.001, 0.001, 0.001],
                       rtol=0.0001)

    print 'wax content:'
    pp.pprint(rec.wax_content)
    assert np.allclose([c['fraction'] for c in rec.wax_content],
                       [0.00504, 0.00641, 0.00594, 0.00533],
                       rtol=0.0001)

    print 'benzene content:'
    pp.pprint(rec.benzene_content)

    assert np.allclose([c['benzene_ppm'] for c in rec.benzene_content],
                       [130L, 50L, 10L, 0L],
                       rtol=0.0001)

    assert np.allclose([c['toluene_ppm'] for c in rec.benzene_content],
                       [1170L, 830L, 40L, 0L],
                       rtol=0.0001)

    assert np.allclose([c['ethylbenzene_ppm'] for c in rec.benzene_content],
                       [510L, 460L, 130L, 0L],
                       rtol=0.0001)

    print 'sara total fractions:'
    pp.pprint(rec.sara_total_fractions)

    assert np.allclose([f['fraction']
                        for f in rec.sara_total_fractions
                        if f['sara_type'] == 'Saturates'],
                       [0.7901, 0.7845, 0.7704, 0.7412],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in rec.sara_total_fractions
                        if f['sara_type'] == 'Aromatics'],
                       [0.13160, 0.13261, 0.134498, 0.134399],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in rec.sara_total_fractions
                        if f['sara_type'] == 'Resins'],
                       [0.071415, 0.076691, 0.088457, 0.11271],
                       rtol=0.0001)
    assert np.allclose([f['fraction']
                        for f in rec.sara_total_fractions
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


def test_access_west(rec):
    '''
        Test an Environment Canada Record ('Access West Winter Blend')

        We added testing for this record specifically because the Alaminos
        record has no emulsion information.
    '''
    print
    print 'name: {}'.format(rec.name)
    print 'weathered: {}'.format(rec.weathering)
    print 'reference: {}'.format(rec.reference)

    print 'emulsions:'
    pp.pprint(rec.emulsions)

    assert np.allclose([d['water_content_fraction'] for d in rec.emulsions],
                       [0.397867, 0.350256, 0.3, 0.0640556,
                        0.1559222, 0.2417778, 0.2997333, 0.0601167],
                       rtol=0.0001)

    assert np.allclose([d['age_days'] for d in rec.emulsions],
                       [0.0, 0.0, 0.0, 0.0, 7.0, 7.0, 7.0, 7.0],
                       rtol=0.0001)

    assert np.allclose([d['ref_temp_k'] for d in rec.emulsions],
                       [288.15] * 8,
                       rtol=0.0001)

    for label in ('water_content_w_w',):
        assert all([label not in v
                    for v in rec.emulsions])
