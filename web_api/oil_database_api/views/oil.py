""" Cornice services.
"""
from itertools import zip_longest
import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPConflict,
                                    HTTPUnsupportedMediaType)

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from oil_database.util.json import fix_bson_ids
from oil_database.models.oil.validation.validate import validate

from oil_database_api.common.views import (cors_policy,
                                           obj_id_from_url)

logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oils*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


# fixme: this could be a class attribute, and make memoize a class
#        might be good to mange the cache better, etc.
#        and keep all the functionality together
#        e.g. clearing the cache when the record changes
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


def decamelize(str_in):
    ret = []
    words = []
    start = 0

    try:
        for i, (l, r) in enumerate(zip_longest(str_in, str_in[1:])):
            if i > 0 and not l.isupper() and r is not None and r.isupper():
                words.append(str_in[start:i+1])
                start = i + 1
            elif i > 0 and l.isupper() and r is not None and not r.isupper():
                words.append(str_in[start:i])
                start = i

        words.append(str_in[start:])
    except Exception:
        return None

    for i, w in enumerate(words):
        if w[-1] == '.':
            ret.append(w)
        elif i == len(words) - 1:
            ret.append(w)
        else:
            ret.extend([w, '_'])

    return ''.join([w.lower() for w in ret])


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

    logger.info('GET /oils: id: {}, options: {}'
                .format(obj_id, request.GET))

    oils = request.db.oil_database.oil

    if obj_id is not None:
        res = oils.find_one({'_id': obj_id})

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
            raise HTTPBadRequest(e)

        search_opts, post_opts = get_search_params(request)
        sort = get_sort_params(request)

        if len(post_opts.keys()) > 0:
            return json_api_results(*search_with_post_sort(oils,
                                                           start, stop,
                                                           search_opts,
                                                           post_opts,
                                                           sort))
        else:
            return json_api_results(*search_with_sort(oils,
                                                      start, stop,
                                                      search_opts, sort))


def json_api_results(results, total):
    return {'data': results,
            'meta': {'total': total}
            }


def search_with_sort(oils, start, stop, search_opts, sort_opts):
    total = oils.count_documents(search_opts)
    logger.info('search #rows: {}'.format(total))

    cursor = oils.find(search_opts)

    if len(sort_opts) > 0:
        cursor = (cursor
                  .collation({
                      'locale': 'en_US',
                      'strength': 1,
                  })
                  .sort(sort_opts)
                  )

    return [[get_oil_searchable_fields(o)
             for i, o in enumerate(cursor)
             if i >= start and i < stop],
            total]


def search_with_post_sort(oils, start, stop, search_opts, post_opts, sort):
    '''
        Apply our sort options after the database query.  This is very slow
        compared to simply applying the sort to the database query itself,
        but is necessary on a couple fields because the value cannot be
        determined until after the record is fetched.
    '''
    logger.info('post-sort...')

    if len(sort) >= 1 and len(sort[0]) >= 2:
        field, direction = sort[0]
    else:
        field, direction = 'metadata.name', ASCENDING

    cursor = oils.find(search_opts)

    results = []
    none_results = []

    for o in cursor:
        rec = get_oil_searchable_fields(o)

        if 'apis' in post_opts:
            # filter out the apis that don't match our criteria
            low, high = post_opts['apis']
            rec_attrs = rec['attributes']

            if ('API' not in rec_attrs['metadata'] or
                    rec_attrs['metadata']['API'] is None or
                    not low <= rec_attrs['metadata']['API'] <= high):
                continue

        if 'labels' in post_opts:
            # filter out the categories that don't match our criteria
            if rec_attrs['metadata']['labels'] is None:
                continue

            labels = [l.lower() for l in post_opts['labels']]
            rec_labels = [c.lower() for c in rec_attrs['metadata']['labels']]

            if not all([(l in rec_labels) for l in labels]):
                continue

        if deep_get(rec_attrs, field) is not None:
            results.append(rec)
        else:
            none_results.append(rec)

    sorted_res = sorted(results,
                        key=lambda x: deep_get(x['attributes'], field),
                        reverse=(direction == DESCENDING))

    if direction == ASCENDING:
        agg_results = none_results + sorted_res
    else:
        agg_results = sorted_res + none_results

    total = len(agg_results)

    return [[o for i, o in enumerate(agg_results)
             if i >= start and i < stop],
            total]


def get_search_params(request):
    '''
        Process the incoming search directives and convert them into MongoDB
        compatible search parameters.

        query options:
        - q: A string that is matched against the oil name, location.  The
             matching will be case insensitive.
        - qApi: A range of numbers in which the API of the oil will be
                filtered.
        - qLabels: A list of label strings that will be matched against the oil
                   labels to filter the results.

        Note: some search directives cannot be easily turned into a MongoDB
              search, so instead they will be used to filter the results.
    '''
    query_out = {}
    post_out = {}

    query = request.GET.get('q', '')

    if query != '':
        query_out.update({
            "$or": [{'metadata.name': {'$regex': query,
                                       '$options': 'i'}},
                    {'metadata.location': {'$regex': query,
                                           '$options': 'i'}}]
        })

    try:
        apis = request.GET.get('qApi', '').split(',')
        low, high = [float(a) for a in apis]

        if low > high:
            low, high = high, low

        post_out['apis'] = [low, high]
    except Exception:
        # couldn't parse items into float interval.  Continue without adding
        # the post-processing step.
        pass

    labels = request.GET.get('qLabels', '')

    if labels != '':
        labels = labels.split(',')
        post_out['labels'] = labels

    return query_out, post_out


def get_sort_params(request):
    '''
        Note: Most of the fields that we want to sort on are now found in the
              metadata attribute.  So to do a MongoDB sort, we need to
              specify the full field path in dotted notation.
    '''
    sort = request.GET.get('sort', None)
    print(f'sort params: {sort}')

    if sort == 'id':
        sort = '_id'
    elif sort == 'api':
        sort = 'metadata.API'

    direction = ({'asc': ASCENDING,
                  'desc': DESCENDING}.get(request.GET.get('dir', 'asc'),
                                          ASCENDING))

    logger.info('(sort, direction): ({}, {})'.format(sort, direction))

    if sort is None:
        return []
    else:
        return [(sort, direction)]


@oil_api.post()
def insert_oil(request):
    logger.info('POST /oils')

    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception as e:
        raise HTTPBadRequest(e)

    try:
        validate(json_obj)
    except Exception as e:  # anything goes wrong with the validation
        # note: ideally the validation should NEVER raise an Exception!
        # but if it does, we need to log it
        # There is no obj_id here -- is there something else we can put
        # in the log?
        # logger.error(f'Validation Error: {obj_id}: {e}')
        logger.error(f'Validation Error: {e}')

    try:
        logger.info('oil.name: {}'.format(json_obj['name']))

        if 'oil_id' in json_obj:
            json_obj['_id'] = json_obj['oil_id']
        else:
            json_obj['_id'] = json_obj['oil_id'] = new_oil_id(request)

        json_obj['_id'] = (request.db.oil_database.oil
                           .insert_one(json_obj)
                           .inserted_id)
    except DuplicateKeyError as e:
        raise HTTPConflict(detail=e)
    except Exception as e:
        logger.error(e)
        raise HTTPUnsupportedMediaType(detail=e)

    return fix_bson_ids(json_obj)


@oil_api.put()
def update_oil(request):
    # ember JSON serializer PUTs the id of the object in the URL
    obj_id = obj_id_from_url(request)

    logger.info('PUT /oils: id: {}'.format(obj_id))

    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception:
        raise HTTPBadRequest

    try:
        oil_obj = get_oil_from_json_req(json_obj)
        fix_oil_id(oil_obj, obj_id)
        try:
            validate(oil_obj)
        except Exception as e:  # anything goes wrong with the validation
            logger.error(f'Validation Error: {obj_id}: {e}')
        (request.db.oil_database.oil
         .replace_one({'_id': oil_obj['_id']}, oil_obj))

        memoized_results.pop(oil_obj['_id'], None)
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return generate_jsonapi_response_from_oil(fix_bson_ids(oil_obj))


@oil_api.patch()
def patch_oil(request):
    '''
        This seems kinda new.
        It is apparently used for partial record updates, and is what the
        ember JSON-API adapters use when updating records.

        https://tools.ietf.org/html/rfc5789#section-2
    '''
    return update_oil(request)


@oil_api.delete()
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:

        res = (request.db.oil_database.oil
               .delete_one({'_id': obj_id}))

        if res.deleted_count == 0:
            raise HTTPNotFound()

        memoized_results.pop(obj_id, None)

        return res
    else:
        raise HTTPBadRequest


def new_oil_id(request):
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

    cursor = (request.db.oil_database.oil
              .find({'_id': {'$regex': '^{}'.format(id_prefix)}}, {'_id'}))
    for row in cursor:
        oil_id = row['_id']

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
    oil_obj['_id'] = json_obj['data']['_id']

    return oil_obj


def fix_oil_id(oil_json, obj_id=None):
    '''
        Okay, pymongo lets you specify the id of a new record, but it needs
        to be the '_id' field. So we need to ensure that the '_id' field
        exists.
        The rule then is that:
        - Ember json serializer PUTs the id in the URL, so we look for it there
          first.
        - the 'oil_id' is a required field, and the '_id' field will be copied
          from it.
    '''
    if obj_id is not None:
        oil_json['_id'] = oil_json['oil_id'] = obj_id
    elif 'oil_id' in oil_json:
        oil_json['_id'] = oil_json['oil_id']
    else:
        raise ValueError('oil_id field is required')


def generate_jsonapi_response_from_oil(oil_obj):
    json_obj = {'data': {'attributes': oil_obj}}

    json_obj['data']['_id'] = oil_obj['_id']
    json_obj['data']['type'] = 'oils'

    return json_obj


def deep_get(rec, path):
    if isinstance(path, str):
        path = path.split('.')

    if len(path) == 1:
        return rec[path[0]]
    else:
        return deep_get(rec[path[0]], path[1:])


@memoize_oil_arg
def get_oil_searchable_fields(oil):
    '''
    Since end users are updating records in an immediate (blur) fashion,
    there could be many records that are only partially filled in.
    So we need to be very tolerant of bad records here.

    However, searching on bad records being bad is, well, OK.
    As long as it doesn't crash
    '''
    # unpack the relevant fields
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
                        'labels': meta.get('labels', []),
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
    return {
        'data': {'_id': oil.get('oil_id'),
                 'type': 'oils',
                 'attributes': oil},
        }
