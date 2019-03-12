#
# This is where we handle the initialization of the imported oil record
# objects that come from the Filemaker database.
#
# Basically, we take the parsed record from our OilLib flat file, and
# find a place for all the data.
#
import sys
import re
import logging

from slugify import slugify_filename

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from ..util.term import TermColor as tc
from ..data_sources.oil_library import OilLibraryFile

from ..models.imported_rec import (ImportedRecord,
                                   Synonym, Density, KVis, DVis, Cut,
                                   Toxicity)

logger = logging.getLogger(__name__)


def add_imported_records(settings):
    '''
        Add our imported records from their associated data sources.
        Right now the only data source is the OilLib file.
    '''
    for fn in settings['oillib.files'].split('\n'):
        logger.info('opening file: {0} ...'.format(fn))
        fd = OilLibraryFile(fn)
        logger.info('file version: {}'.format(fd.__version__))

        print('Adding new records to database')

        rowcount = 0
        for r in fd.readlines():
            if len(r) < 10:
                logger.info('got record: {}'.format(r))

            r = [unicode(f, 'utf-8') if f is not None else f
                 for f in r]

            try:
                add_imported_record(fd.file_columns, r)
            except ValidationError as e:
                rec_id = tc.change(r[fd.file_columns_lu['ADIOS_Oil_ID']],
                                   'red')
                print ('validation failed for {}: {}'.format(rec_id, e))
            except DuplicateKeyError as e:
                rec_id = tc.change(r[fd.file_columns_lu['ADIOS_Oil_ID']],
                                   'red')
                print ('duplicate fields for {}: {}'.format(rec_id, e))

            if rowcount % 100 == 0:
                sys.stderr.write('.')

            rowcount += 1

        print('finished!!!  {0} rows processed.'.format(rowcount))


def add_imported_record(file_columns, row_data):
    '''
        Add a record from the NOAA filemaker export flatfile.
    '''
    file_columns = [slugify_filename(c).lower()
                    for c in file_columns]
    row_dict = dict(zip(file_columns, row_data))

    fix_id(row_dict)
    fix_name(row_dict)

    fix_location(row_dict)
    fix_field_name(row_dict)
    add_record_date(row_dict)

    fix_pour_point(row_dict)
    fix_flash_point(row_dict)
    fix_preferred_oils(row_dict)

    ir = ImportedRecord(**row_dict)

    add_synonyms(ir, row_dict)
    add_densities(ir, row_dict)
    add_kinematic_viscosities(ir, row_dict)
    add_dynamic_viscosities(ir, row_dict)
    add_distillation_cuts(ir, row_dict)
    add_toxicity_effective_concentrations(ir, row_dict)
    add_toxicity_lethal_concentrations(ir, row_dict)

    ir.save()


def fix_id(kwargs):
    kwargs['oil_id'] = kwargs['adios_oil_id'].strip()
    del kwargs['adios_oil_id']


def fix_name(kwargs):
    kwargs['oil_name'] = kwargs['oil_name'].strip()


def fix_location(kwargs):
    ''' just to maintain our uniqueness constraint '''
    if kwargs['location'] is None:
        kwargs['location'] = ''
    else:
        kwargs['location'] = kwargs['location'].strip()


def fix_field_name(kwargs):
    ''' just to maintain our uniqueness constraint '''
    if kwargs['field_name'] is None:
        kwargs['field_name'] = ''
    else:
        kwargs['field_name'] = kwargs['field_name'].strip()


def add_record_date(kwargs):
    '''
        Search the reference field looking for any 4 digit numeric values.
        We will assume these to be possible years of publication.
    '''
    if kwargs['reference'] is None:
        ref_dates = ['no-ref']
    else:
        p = re.compile(r'\d{4}')
        m = p.findall(kwargs['reference'])
        if len(m) == 0:
            ref_dates = ['no-date']
        else:
            ref_dates = m

    kwargs['reference_date'] = ', '.join(list(set(ref_dates)))


def fix_pour_point(kwargs):
    # kind of weird behavior...
    # pour_point min-max values have the following configurations:
    #     ['<', value] which means "less than" the max value
    #                  We will make it ['', value]
    #                  since max is really a max
    #     ['>', value] which means "greater than" the max value
    #                  We will make it [value, '']
    #                  since max is really a min
    if kwargs.get('pour_point_min_k') == '<':
        kwargs['pour_point_min_k'] = None
    if kwargs.get('pour_point_min_k') == '>':
        kwargs['pour_point_min_k'] = kwargs['pour_point_max_k']
        kwargs['pour_point_max_k'] = None


def fix_flash_point(kwargs):
    # same kind of weird behavior as pour point...
    if kwargs.get('flash_point_min_k') == '<':
        kwargs['flash_point_min_k'] = None
    if kwargs.get('flash_point_min_k') == '>':
        kwargs['flash_point_min_k'] = kwargs['flash_point_max_k']
        kwargs['flash_point_max_k'] = None


def fix_preferred_oils(kwargs):
    kwargs['preferred_oils'] = (True if kwargs.get('preferred_oils') == 'X'
                                else False)


def add_synonyms(oil, row_dict):
    if ('synonyms' in row_dict and
            row_dict['synonyms'] is not None):
        synonyms = [s.strip() for s in row_dict.get('synonyms').split(',')]
        oil.synonyms.extend(set([Synonym(name=s)
                                 for s in synonyms
                                 if len(s) > 0]))


def add_densities(oil, row_dict):
    for i in range(1, 5):
        obj_args = ('kg_m_3', 'ref_temp_k', 'weathering')
        row_fields = ['density{}_{}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            densityargs = {}

            for col, arg in zip(row_fields, obj_args):
                densityargs[arg] = row_dict.get(col)

            oil.densities.append(Density(**densityargs))


def add_kinematic_viscosities(oil, row_dict):
    for i in range(1, 7):
        obj_args = ('m_2_s', 'ref_temp_k', 'weathering')
        row_fields = ['kvis{}_{}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            kvisargs = {}

            for col, arg in zip(row_fields, obj_args):
                kvisargs[arg] = row_dict.get(col)

            oil.kvis.append(KVis(**kvisargs))


def add_dynamic_viscosities(oil, row_dict):
    for i in range(1, 7):
        obj_args = ('kg_ms', 'ref_temp_k', 'weathering')
        row_fields = ['dvis{}_{}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            dvisargs = {}

            for col, arg in zip(row_fields, obj_args):
                dvisargs[arg] = row_dict.get(col)

            oil.dvis.append(DVis(**dvisargs))


def add_distillation_cuts(oil, row_dict):
    for i in range(1, 16):
        obj_args = ('vapor_temp_k', 'liquid_temp_k', 'fraction')
        row_fields = ['cut{0}_{1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            cutargs = {}

            for col, arg in zip(row_fields, obj_args):
                cutargs[arg] = row_dict.get(col)

            oil.cuts.append(Cut(**cutargs))


def add_toxicity_effective_concentrations(oil, row_dict):
    for i in range(1, 4):
        obj_args = ('species', '24h', '48h', '96h')
        row_fields = ['tox_ec{0}_{1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            toxargs = {}
            toxargs['tox_type'] = 'EC'

            for col, arg in zip(row_fields, obj_args):
                if arg[0].isdigit():
                    # table column names cannot start with a digit
                    arg = 'after_{0}'.format(arg)
                toxargs[arg] = row_dict.get(col)

            oil.toxicities.append(Toxicity(**toxargs))


def add_toxicity_lethal_concentrations(oil, row_dict):
    for i in range(1, 4):
        obj_args = ('species', '24h', '48h', '96h')
        row_fields = ['tox_lc{0}_{1}'.format(i, a) for a in obj_args]

        if any([row_dict.get(k) for k in row_fields]):
            toxargs = {}
            toxargs['tox_type'] = 'LC'

            for col, arg in zip(row_fields, obj_args):
                if arg[0].isdigit():
                    # table column names cannot start with a digit
                    arg = 'after_{0}'.format(arg)
                toxargs[arg] = row_dict.get(col)

            oil.toxicities.append(Toxicity(**toxargs))
