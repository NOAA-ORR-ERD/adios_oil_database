""" Cornice services.
"""
import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from pymongo import ASCENDING, DESCENDING

from oil_database.util.json import fix_bson_ids
from oil_database.data_sources.oil import OilEstimation

from oil_database_api.common.views import (cors_policy,
                                           obj_id_from_url)

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oils*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


def memoize_oil_arg(func):
    '''
        Decorator function to cache function results by oil_id
    '''
    results = {}

    def memoized_func(oil):
        key = oil['oil_id']

        if key not in results:
            logger.info('loading Key: "{}"'.format(key))
            results[key] = func(oil)

        return results[key]

    return memoized_func


def decamelize(str_in):
    words = []
    start = 0

    try:
        for i, c in enumerate(str_in):
            if c.isupper() and i > 0:
                words.append(str_in[start:i])
                start = i

        words.append(str_in[start:])
    except Exception:
        return None

    return '_'.join([w.lower() for w in words])


@oil_api.get()
def get_oils(request):
    '''
        We will do one of two possible things here.
        1. Return the searchable fields for all oils in JSON format.
        2. Return the JSON record of a particular oil.

        GET OPTIIONS:
        - limit: The max number of result items
        - page: The page number {0...N} of result items. (pagesize = limit)
    '''
    obj_id = obj_id_from_url(request)

    logger.info('GET /oils: id: {} options: {}'
                .format(obj_id, request.GET))

    oils = request.db.oil_database.oil

    if obj_id is not None:
        res = oils.find_one({'_id': obj_id})

        if res is not None:
            return res
        else:
            raise HTTPNotFound()
    else:
        try:
            limit, page = [int(o) for o in (request.GET.get('limit', '0'),
                                            request.GET.get('page', '0'))]
            start, stop = [limit * i for i in (page, page + 1)]
            logger.info('start, stop = {}, {}'.format(start, stop))
        except Exception as e:
            raise HTTPBadRequest(e)

        search_opts = search_params(request)
        sort = sort_params(request)

        if (len(sort) > 0 and
                sort[0][0] in ('apis', 'categories_str', 'viscosity')):
            return list(search_with_post_sort(oils,
                                              start, stop,
                                              search_opts, sort))
        else:
            return list(search_with_sort(oils,
                                         start, stop,
                                         search_opts, sort))


def search_with_sort(oils, start, stop, search_opts, sort_opts):
    cursor = oils.find(search_opts)

    if len(sort_opts) > 0:
        cursor = cursor.sort(sort_opts)

    logger.info('cursor #rows: {}'.format(cursor.count()))

    return [get_oil_searchable_fields(o)
            for i, o in enumerate(cursor)
            if i >= start and i < stop]


def search_with_post_sort(oils, start, stop, search_opts, sort):
    '''
        Apply our sort options after the database query.  This is very slow
        compared to simply applying the sort to the database query itself,
        but is necessary on a couple fields because the value cannot be
        determined until after the record is fetched.
    '''
    logger.info('post-sort...')
    field, direction = sort[0]

    cursor = oils.find(search_opts)

    results = []
    none_results = []

    for o in cursor:
        rec = get_oil_searchable_fields(o)
        if rec[field] is not None:
            results.append(rec)
        else:
            none_results.append(rec)

    sorted_res = sorted(results,
                        key=lambda x: x[field],
                        reverse=(direction == DESCENDING))

    if direction == ASCENDING:
        agg_results = none_results + sorted_res
    else:
        agg_results = sorted_res + none_results

    return [o for i, o in enumerate(agg_results)
            if i >= start and i < stop]


def sort_params(request):
    sort = decamelize(request.GET.get('sort', None))
    direction = ({'asc': ASCENDING,
                  'desc': DESCENDING}.get(request.GET.get('dir', 'asc'),
                                          ASCENDING))

    logger.info('(sort, direction): ({}, {})'.format(sort, direction))

    if sort is None:
        return []
    else:
        return [(sort, direction)]


def search_params(request):
    query = request.GET.get('q', '')
    field_name = decamelize(request.GET.get('qAttr', ''))

    logger.info('(query, field_name): ({}, {})'.format(query, field_name))

    if query != '' and field_name != '':
        logger.info('full search params')
        return {field_name: {'$regex': query,
                             '$options': 'i'}}
    else:
        logger.info('empty search params')
        return {}


@oil_api.post()
def insert_oil(request):
    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception as e:
        raise HTTPBadRequest(e)

    try:
        fix_oil_id(json_obj)

        json_obj['_id'] = (request.db.oil_database.oil
                           .insert_one(json_obj)
                           .inserted_id)
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return fix_bson_ids(json_obj)


@oil_api.put()
def update_oil(request):
    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception:
        raise HTTPBadRequest

    try:
        fix_oil_id(json_obj)

        (request.db.oil_database.oil
         .replace_one({'_id': json_obj['_id']}, json_obj))
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return fix_bson_ids(json_obj)


@oil_api.delete()
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:

        res = (request.db.oil_database.oil
               .delete_one({'_id': obj_id}))

        if res.deleted_count == 0:
            raise HTTPNotFound()

        return res
    else:
        raise HTTPBadRequest


def fix_oil_id(oil_json):
    '''
        Okay, pymongo lets you specify the id of a new record, but it needs
        to be the '_id' field. So we need to ensure that the '_id' field
        exists.
        The rule then is that the 'oil_id' is a required field, and the '_id'
        field will be copied from it.
    '''
    if 'oil_id' in oil_json:
        oil_json['_id'] = oil_json['oil_id']
    else:
        raise ValueError('oil_id field is required')


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    oil = OilEstimation(oil)
    sample = oil.get_sample()

    if sample is None:
        # maybe there is not an unweathered (fresh) sample?
        # That's ok, we will just get the first one we see.
        sample = oil.get_first_sample()

    try:
        return {'_id': oil.oil_id,
                'name': oil.name,
                'location': oil.location,
                'product_type': oil.product_type,
                'apis': [sample.get_api()],
                'pour_point': sample.pour_point(),
                'viscosity': sample.kvis_at_temp(273.15 + 38),
                'categories': oil.categories,
                'status': oil.status,
                }
    except Exception:
        logger.info('oil failed searchable fields: {}: {}'
                    .format(oil.oil_id, oil.name))
        raise
