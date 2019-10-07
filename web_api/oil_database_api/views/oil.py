""" Cornice services.
"""
import re
import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from pymongo import ASCENDING, DESCENDING
from bson.errors import InvalidId

from oil_database.util.json import jsonify_model_obj, ObjFromDict
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
        res = get_oil_dict(oils, obj_id)

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

    sorted_res = sorted([get_oil_searchable_fields(o)
                         for o in cursor],
                        key=lambda x: x[field],
                        reverse=(direction == DESCENDING))

    return [o for i, o in enumerate(sorted_res)
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
        obj = Oil(**json_obj)
        obj.save()
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return jsonify_model_obj(obj)


@oil_api.put()
def update_oil(request):
    '''
        The mongo model classes implement 'upsert' behavior, which is to say
        that if the record exists, it is updated, and if it does not exist,
        then it is inserted.
        So this function, although separate, looks very similar to the insert
        function.
    '''
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
        obj = Oil(**json_obj)
        obj.save()
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return jsonify_model_obj(obj)


@oil_api.delete()
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        res = get_one_oil(obj_id)

        if res is None:
            raise HTTPNotFound()
        else:
            # should maybe wrap this in a try, and return any failure response
            return res.delete()
    else:
        raise HTTPBadRequest


def fix_oil_id(oil_json):
    '''
        Okay, this is some weirdness with the PyMODM models.  You can use a
        custom field as a primary key, and we have done this with the oil_id
        field.  But when the object is retrieved, the primary key field will
        always be '_id', not the custom field name.
        And if we assume an insert/update return trip workflow, we can also
        assume in those cases that the oil_id will have been renamed.
        So we will rename it back to 'oil_id'.
    '''
    if '_id' in oil_json:
        oil_json['oil_id'] = oil_json['_id']
        del oil_json['_id']


def get_one_oil(obj_id):
    try:
        result = Oil.find_one({'oil_id': obj_id})
    except InvalidId:
        return None

    if isinstance(result, Oil):
        return result
    elif len(result) > 0:
        return result[0]


def get_oil_dict(obj_id):
    return jsonify_model_obj(get_one_oil(obj_id))


def get_oil_non_embedded_docs(oil_dict):
    '''
        Custom routine to retrieve any non-embedded documents that are
        referenced by our oil attributes.

        Right now we are handling:
        - categories
    '''
    for i, c in enumerate(oil_dict['categories']):
        oil_dict['categories'][i] = (Category.find_one({'_id': c}).dict())


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    pp.pprint(oil)
    oil = OilEstimation(oil)

    try:
        return {'_id': oil.oil_id,
                'name': oil.name,
                'location': oil.location,
                'product_type': oil.product_type,
                'apis': [a for a in oil.apis],
                'pour_point': oil.pour_point(),
                'viscosity': oil.kvis_at_temp(273.15 + 38),
                'categories': oil.categories,
                'status': oil.status,
                }
    except Exception:
        logger.info('oil failed searchable fields: {}: {}'
                    .format(oil.oil_id, oil.name))
        raise


def get_category_ids(oil):
    return [jsonify_model_obj(c)['_id'] for c in oil.categories]


def get_category_paths_str(oil, sep=','):
    regex = re.compile(r'\b(Crude-|Refined-|Other-)\b')

    cat_str = sep.join(sorted(set(get_category_paths(oil))))

    return regex.sub("", cat_str)


def get_category_paths(oil, sep='-'):
    return [sep.join([c.name for c in get_category_ancestors(cat)])
            for cat in oil.categories]


def get_category_ancestors(category):
    '''
        Here we take a category, which is assumed to be a node
        in a tree structure, and determine the parents of the category
        all the way up to the apex.
    '''
    cat_list = []
    cat_list.append(category)

    while category.parent is not None:
        cat_list.append(category.parent)
        category = category.parent

    cat_list.reverse()
    return cat_list


def get_synonyms(oil, sep=','):
    syn_list = [s.name for s in oil.synonyms]

    return sep.join(syn_list)
