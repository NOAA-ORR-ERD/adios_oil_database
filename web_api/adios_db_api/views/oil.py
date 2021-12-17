"""
Cornice Oil services.
"""
import sys
import logging
import traceback

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPNoContent,
                                    HTTPConflict,
                                    HTTPUnsupportedMediaType,
                                    HTTPInternalServerError)

from pymongo.errors import DuplicateKeyError

from adios_db.models.oil.validation.validate import validate_json
from adios_db.models.oil.completeness import set_completeness

from adios_db_api.common.views import (cors_policy,
                                       obj_id_from_url,
                                       can_modify_db)

logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oils/*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


memoized_results = {}  # so it is visible to other functions
temp_oils = {}  # we need to persist our temporary oils somewhere


def memoize_oil_arg(func):
    """
    Decorator function to cache function results by oil_id
    """
    def memoized_func(oil):
        key = oil['oil_id']

        if key not in memoized_results:
            logger.info('loading Key: "{}"'.format(key))
            memoized_results[key] = func(oil)

        return memoized_results[key]

    return memoized_func


@oil_api.get()
def get_oils(request):
    """
    We will do one of two possible things here.
    1. Return the searchable fields for all oils in JSON format.
    2. Return the JSON record of a particular oil.
    """
    obj_id = obj_id_from_url(request)

    logger.info('GET /oils: id: {}, options: {}'.format(obj_id, request.GET))

    adb_session = request.adb_session

    if obj_id is not None:
        res = adb_session.find_one(obj_id)

        if res is None:
            res = temp_oils.get(obj_id, None)

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
            return json_api_results(adb_session.query(page=[start, stop],
                                                      sort=sort,
                                                      **search_opts),
                                    limit)
        except Exception as e:
            logger.error(e)
            raise HTTPInternalServerError(e)


def json_api_results(results, page_size):
    total = len(results)  # .count()
    pages = total / page_size if page_size > 0 else 1

    data = [get_oil_searchable_fields(r) for r in results]

    ret = {'data': data,
           'meta': {'total': total,
                    'totalPages': pages}
           }

    return ret


def get_search_params(request):
    """
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
    """
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
    """
    Note: Most of the fields that we want to sort on are now found in the
          metadata attribute.  So to do a MongoDB sort, we need to
          specify the full field path in dotted notation.
    """
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
            oil_obj['oil_id'] = request.adb_session.new_oil_id()

        oil = validate_json(oil_obj)
        set_completeness(oil)

        if is_temp_id(oil.oil_id):
            logger.info(f"Temporary oil with ID: {oil.oil_id}, "
                        "persisting in memory, not the database.")
            oil_json = oil.py_json()
            oil_json['_id'] = oil.oil_id
            temp_oils[oil.oil_id] = oil_json
        else:
            mongo_id = request.adb_session.insert_one(oil)

            logger.info(f'Insert oil with mongo ID: {mongo_id}, '
                        f'oil ID: {oil.oil_id}')
    except DuplicateKeyError as e:
        logger.error(e)
        raise HTTPConflict('Insert failed: Duplicate Key')
    except Exception as e:
        logger.error(e)
        raise HTTPUnsupportedMediaType("Unknown Error")

    return generate_jsonapi_response_from_oil(oil.py_json())


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

        if is_temp_id(oil.oil_id):
            logger.info(f"Temporary oil with ID: {oil.oil_id}, "
                        "update it in memory, not the database.")
            temp_oils[oil.oil_id] = oil.py_json()
        else:
            request.adb_session.replace_one(oil)
            memoized_results.pop(oil.oil_id, None)

            logger.info(f'Update oil with ID: {oil.oil_id}')
    except Exception as e:
        logger.error(e)
        raise HTTPUnsupportedMediaType()

    return generate_jsonapi_response_from_oil(oil.py_json())


def is_temp_id(oil_id):
    '''
        We will support temporary IDs, in which we will treat the JSON object
        coming inside the request as a temporary object.  So we will treat it
        in the same manner as any other oil object, but we will not store it
        in the database.
        Temporary IDs are defined as having a suffix that is unchanging and
        well known.
    '''
    return oil_id.endswith('-TEMP')


def _trace_item(filename, lineno, function, text):
    """
    Package up the trace item information into a py_json struct.
    Mainly this keeps the traceback parsing loop cleaner.
    """
    return {'file': filename,
            'lineno': lineno,
            'function': function,
            'text': text}


@oil_api.patch()
@can_modify_db
def patch_oil(request):
    """
    This seems kinda new.
    It is apparently used for partial record updates, and is what the
    ember JSON-API adapters use when updating records.

    https://tools.ietf.org/html/rfc5789#section-2
    """
    return update_oil(request)


@oil_api.delete()
@can_modify_db
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        if obj_id in temp_oils:
            del temp_oils[obj_id]
        else:
            res = request.adb_session.delete_one(obj_id)

            if res.deleted_count == 0:
                raise HTTPBadRequest()  # JSONAPI expects this upon failure

            memoized_results.pop(obj_id, None)

        raise HTTPNoContent()  # JSONAPI expects this upon success
    else:
        raise HTTPBadRequest()  # JSONAPI expects this upon failure


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
    json_obj['data']['attributes']['status'] = oil_obj.get('status', [])

    return json_obj


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    """
    Since end users are updating records in an immediate (blur) fashion,
    there could be many records that are only partially filled in.
    So we need to be very tolerant of bad records here.

    However, searching on bad records being bad is, well, OK.
    As long as it doesn't crash
    """
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
    """
    Get the full record in JSON API compliant form.
    """
    logger.info(f'oil object oil_id: {oil["oil_id"]}')
    oil.pop('_id', None)

    return {
        'data': {
            '_id': oil.get('oil_id'),
            'type': 'oils',
            'attributes': oil},
        }
