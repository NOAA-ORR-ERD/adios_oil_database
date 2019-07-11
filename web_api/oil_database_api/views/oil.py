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

from pymodm.errors import DoesNotExist
from bson.errors import InvalidId

from oil_database.util.json import jsonify_model_obj
from oil_database.data_sources.oil import OilEstimation
from oil_database.models.common import Category
from oil_database.models.oil import Oil

from oil_database_api.common.views import cors_policy, obj_id_from_url


logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oils*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


def memoize_oil_arg(func):
    results = {}

    def memoized_func(oil):
        if oil.oil_id not in results:
            logger.info('loading Key: "{}"'
                        .format(oil.oil_id))
            results[oil.oil_id] = func(oil)

        return results[oil.oil_id]

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

    if obj_id is not None:
        res = get_oil_dict(obj_id)

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

        try:
            sort = sort_params(request)
        except Exception as e:
            raise HTTPBadRequest(e)

        search_opts = search_params(request)

        if (len(sort) > 0 and
                sort[0][0] in ('apis', 'categories_str', 'viscosity')):
            return search_with_post_sort(start, stop, search_opts, sort)
        else:
            return search_with_sort(start, stop, search_opts, sort)


def search_with_sort(start, stop, search_opts, sort):
    cursor = Oil.objects.raw(search_opts).order_by(sort)

    logger.info('cursor #rows: {}'.format(cursor.count()))

    return [get_oil_searchable_fields(o)
            for i, o in enumerate(cursor)
            if i >= start and i < stop]


def search_with_post_sort(start, stop, search_opts, sort):
    '''
        Apply our sort options after the database query.  This is very slow
        compared to simply applying the sort to the database query itself,
        but is necessary on a couple fields because the value cannot be
        determined until after the record is fetched.
    '''
    logger.info('post-sort...')
    field, direction = sort[0]

    cursor = Oil.objects.raw(search_opts)

    sorted_res = sorted([get_oil_searchable_fields(o)
                         for o in cursor],
                        key=lambda x: x[field],
                        reverse=(direction == DESCENDING))

    return [o for i, o in enumerate(sorted_res)
            if i >= start and i < stop]


def sort_params(request):
    sort = decamelize(request.GET.get('sort', None))
    direction = ({'asc': ASCENDING, 'desc': DESCENDING}
                 .get(request.GET.get('dir', 'asc')))

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
        print e
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
        print e
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
        klass, query_set = Oil, {'_id': obj_id}
        result = klass.objects.get(query_set)
    except (DoesNotExist, InvalidId):
        return None

    if isinstance(result, klass):
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
        oil_dict['categories'][i] = (Category.objects.get({'_id': c})
                                     .to_son().to_dict())


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    oil_estimation = OilEstimation(oil)

    try:
        return {'_id': oil.oil_id,
                'name': oil.name,
                'location': oil.location,
                'product_type': oil.product_type,
                'apis': [a.to_son().to_dict() for a in oil.apis],
                'pour_point': oil_estimation.pour_point(),
                'viscosity': oil_estimation.kvis_at_temp(273.15 + 38),
                'categories': get_category_paths(oil),
                'categories_str': get_category_paths_str(oil),
                'status': oil.status,
                }
    except Exception:
        logger.info('oil failed searchable fields: {}'
                    .format(oil))
        raise


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
