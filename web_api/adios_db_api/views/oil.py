""" Cornice services.
"""
import sys
import logging
import traceback

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPConflict,
                                    HTTPUnsupportedMediaType,
                                    HTTPInternalServerError)

from pymongo.errors import DuplicateKeyError

from adios_db.util.json import fix_bson_ids
from adios_db.models.oil.validation.validate import validate_json
from adios_db.models.oil.completeness import set_completeness

from adios_db_api.common.views import (cors_policy,
                                       obj_id_from_url,
                                       can_modify_db)


logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oils/*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


memoized_results = {}  # so it is visible to other functions


def memoize_oil_arg(func):
    '''
        Decorator function to cache function results by oil_id
    '''
    def memoized_func(oil):
        key = oil['oil_id']

        if key not in memoized_results:
            logger.info('loading Key: "{}"'.format(key))
            memoized_results[key] = func(oil)

        return memoized_results[key]

    return memoized_func


@oil_api.get()
def get_oils(request):
    '''
        We will do one of two possible things here.
        1. Return the searchable fields for all oils in JSON format.
        2. Return the JSON record of a particular oil.
    '''
    obj_id = obj_id_from_url(request)

    logger.info('GET /oils: id: {}, options: {}'.format(obj_id, request.GET))

    client = request.mdb_client

    if obj_id is not None:
        # Fixme: why is this not using the adios_db Session?
        res = client.oil.find_one({'oil_id': obj_id})

        if res is not None:
            return get_oil_all_fields(res)
        else:
            raise HTTPNotFound()
    else:
        try:
            limit, page = [int(o) for o in (request.GET.get('limit', '0'),
                                            request.GET.get('page', '0'))]
            start, stop = [limit * i for i in (page, page + 1)]
            logger.info('start, stop = {}, {}'.format(start, stop))
        except Exception as e:
            logger.error(e)
            raise HTTPBadRequest("Could not determine paging range")

        search_opts = get_search_params(request)
        sort = get_sort_params(request)

        try:
            return json_api_results(client.query(page=[start, stop],
                                                 sort=sort,
                                                 **search_opts),
                                    limit)
        except Exception as e:
            logger.error(e)
            raise HTTPInternalServerError(e)


def json_api_results(results, page_size):
    total = results.count()
    pages = total / page_size if page_size > 0 else 1

    data = [get_oil_searchable_fields(r) for r in results]
    ret = {'data': data,
           'meta': {'total': total,
                    'totalPages': pages}
           }

    return ret


def get_search_params(request):
    '''
        Process the incoming search directives and convert them into search
        parameters compatible with Session.query().

        query options:
        - q: A string that is matched against the oil name, location.  The
             matching will be case insensitive.
        - qApi: A range of numbers in which the API of the oil will be
                filtered.
        - qType: The type of oil to match when filtering the results.
        - qLabels: A list of label strings that will be matched against the oil
                   labels to filter the results.
    '''
    query_out = {}
    xform_opts = {'q': 'text',
                  'qApi': 'api',
                  'qType': 'product_type',
                  'qLabels': 'labels',
                  'qGnomeSuitable': 'gnome_suitable'
                  }

    for k, v in request.GET.items():
        if k in xform_opts and v not in (None, ''):
            query_out[xform_opts[k]] = v

    return query_out


def get_sort_params(request):
    '''
        Note: Most of the fields that we want to sort on are now found in the
              metadata attribute.  So to do a MongoDB sort, we need to
              specify the full field path in dotted notation.
    '''
    sort = request.GET.get('sort')
    direction = request.GET.get('dir', 'asc')

    if sort == 'id':
        sort = 'oil_id'
    elif sort == 'api':
        sort = 'metadata.API'

    logger.info('(sort, direction): ({}, {})'.format(sort, direction))

    if sort is None:
        return None
    else:
        return [(sort, direction)]


@oil_api.post()
@can_modify_db
def insert_oil(request):
    logger.info('POST /oils')

    try:
        json_obj = ujson.loads(request.body)

        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception as e:
        logger.error(e)
        raise HTTPBadRequest("Error parsing oil JSON")

    try:
        oil_obj = get_oil_from_json_req(json_obj)
    except Exception as e:
        logger.error(f'Validation Error: {e}')
        raise HTTPBadRequest("Error validating oil JSON")

    try:
        logger.info('oil.name: {}'.format(oil_obj['metadata']['name']))

        if 'oil_id' not in oil_obj:
            oil_obj['oil_id'] = new_oil_id(request)

        oil = validate_json(oil_obj)
        set_completeness(oil)
        oil_obj = oil.py_json()
        oil_obj['_id'] = oil_obj['oil_id']

        mongo_id = (request.mdb_client.oil
                           .insert_one(oil_obj)
                           .inserted_id)
        logger.info(f'insert oil with mongo ID: {mongo_id}, '
                    f'oil ID: {oil_obj["oil_id"]}')
    except DuplicateKeyError as e:
        logger.error(e)
        raise HTTPConflict('Insert failed: Duplicate Key')
    except Exception as e:
        logger.error(e)
        raise HTTPUnsupportedMediaType("Unknown Error")

    return generate_jsonapi_response_from_oil(fix_bson_ids(oil_obj))


@oil_api.put()
@can_modify_db
def update_oil(request):
    # ember JSON serializer PUTs the id of the object in the URL
    obj_id = obj_id_from_url(request)

    logger.info('PUT /oils: id: {}'.format(obj_id))

    try:
        json_obj = ujson.loads(request.body)

        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception:
        raise HTTPBadRequest('Could not parse oil JSON')

    try:
        oil_obj = get_oil_from_json_req(json_obj)

        try:
            oil = validate_json(oil_obj)
        except Exception as e:
            logger.error(f'Validation Exception: '
                         f'{obj_id}: {type(e)}: {e}')

            # There are lots of places where the validation could have raised
            # an exception.  The traceback can tell us where it happened.
            depth = 3
            _, _, exc_traceback = sys.exc_info()
            tb = traceback.extract_tb(exc_traceback)

            if len(tb) > depth:
                tb = tb[-depth:]

            for i in tb:
                logger.error(f'traceback: {_trace_item(*i)}')

        set_completeness(oil)
        oil_obj = oil.py_json()
        (request.mdb_client.oil
         .replace_one({'oil_id': oil_obj['oil_id']}, oil_obj))

        memoized_results.pop(oil_obj['oil_id'], None)
    except Exception as e:
        logger.error(e)
        raise HTTPUnsupportedMediaType()

    return generate_jsonapi_response_from_oil(oil_obj)


def _trace_item(filename, lineno, function, text):
    '''
        Package up the trace item information into a py_json struct.
        Mainly this keeps the traceback parsing loop cleaner.
    '''
    return {'file': filename,
            'lineno': lineno,
            'function': function,
            'text': text}


@oil_api.patch()
@can_modify_db
def patch_oil(request):
    '''
        This seems kinda new.
        It is apparently used for partial record updates, and is what the
        ember JSON-API adapters use when updating records.

        https://tools.ietf.org/html/rfc5789#section-2
    '''
    return update_oil(request)


@oil_api.delete()
@can_modify_db
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:

        res = (request.mdb_client.oil
               .delete_one({'oil_id': obj_id}))

        if res.deleted_count == 0:
            raise HTTPNotFound()

        memoized_results.pop(obj_id, None)

        return res
    else:
        raise HTTPBadRequest()


def new_oil_id(request):
    # fixme: this should be in the adios_db package
    '''
        Query the database for the next highest ID with a prefix of XX
        The current implementation is to walk the oil IDs, filter for the
        prefix, and choose the max numeric content.

        Warning: We don't expect a lot of traffic POST'ing a bunch new oils
                 to the database, it will only happen once in awhile.
                 But this is not the most effective way to do this.
                 A persistent incremental counter would be much faster.
                 In fact, this is a bit brittle, and would fail if the website
                 suffered a bunch of POST requests at once.
    '''
    id_prefix = 'XX'
    max_seq = 0

    cursor = (request.mdb_client.oil
              .find({'oil_id': {'$regex': '^{}'.format(id_prefix)}},
                    {'oil_id'}))

    for row in cursor:
        oil_id = row['oil_id']

        try:
            oil_seq = int(oil_id[len(id_prefix):])
        except ValueError:
            print('ValuError: continuing...')
            continue

        max_seq = oil_seq if oil_seq > max_seq else max_seq

    max_seq += 1  # next in the sequence

    return '{}{:06d}'.format(id_prefix, max_seq)


def get_oil_from_json_req(json_obj):
    oil_obj = json_obj['data']['attributes']

    if 'oil_id' in json_obj['data']:
        # won't have an id if we are inserting
        oil_obj['oil_id'] = json_obj['data']['oil_id']

    return oil_obj


def generate_jsonapi_response_from_oil(oil_obj):
    json_obj = {'data': {'attributes': oil_obj}}

    json_obj['data']['_id'] = oil_obj['oil_id']
    json_obj['data']['type'] = 'oils'

    return json_obj


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    '''
    Since end users are updating records in an immediate (blur) fashion,
    there could be many records that are only partially filled in.
    So we need to be very tolerant of bad records here.

    However, searching on bad records being bad is, well, OK.
    As long as it doesn't crash
    '''
    try:
        meta = oil['metadata']

        # id, type, & attributes are required top-level attributes in order to
        # comply with the JSON API specification for a resource object.
        # source: https://jsonapi.org/format/
        return {'_id': oil.get('oil_id'),
                'type': 'oils',
                'attributes': {
                    'metadata': {
                        'name': meta.get('name', None),
                        'location': meta.get('location', None),
                        'product_type': meta.get('product_type', None),
                        'API': meta.get('API'),
                        'sample_date': meta.get('sample_date', ''),
                        'labels': meta.get('labels', []),
                        'model_completeness': meta.get('model_completeness',
                                                       None),
                        'gnome_suitable': meta.get('gnome_suitable', None),
                    },
                    'status': oil.get('status', []),
                },
                }
    except Exception:
        logger.info('oil failed searchable fields {}: {}'
                    .format(oil['oil_id'], oil['name']))
        raise


def get_oil_all_fields(oil):
    '''
        Get the full record in JSON API compliant form.
    '''
    logger.info(f'oil object _id: {oil["_id"]}')
    oil.pop('_id', None)

    return {
        'data': {
            '_id': oil.get('oil_id'),
            'type': 'oils',
            'attributes': oil},
        }
