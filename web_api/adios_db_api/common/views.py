"""
Common Gnome object request handlers.
"""
import sys
import traceback
import logging

import ujson

from pyramid.httpexceptions import HTTPForbidden

cors_policy = {'credentials': True}

logger = logging.getLogger(__name__)


def obj_id_from_url(request):
    '''
        Get an object ID from the request URL
        - The ID could be contained in link (/object/<id>)
          The pyramid URL parser returns a tuple of 0 or more matching items,
          at least when using the * wild card
        - The ID could also be contained in GET param (/object?id=<id>)
    '''
    obj_id = request.matchdict.get('obj_id')
    obj_id = obj_id[0] if len(obj_id) > 0 else None

    if obj_id is None:
        obj_id = request.GET.get('id', None)

    return obj_id


def obj_id_from_req_payload(json_request):
    return json_request.get('id')


def cors_exception(request, exception_class, with_stacktrace=False):
    depth = 2
    http_exc = exception_class()

    hdr_val = request.headers.get('Origin')
    if hdr_val is not None:
        http_exc.headers.add('Access-Control-Allow-Origin', hdr_val)
        http_exc.headers.add('Access-Control-Allow-Credentials', 'true')

    if with_stacktrace:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        fmt = traceback.format_exception(exc_type, exc_value, exc_traceback)

        http_exc.json_body = ujson.dumps([l.strip() for l in fmt][-depth:])

    return http_exc


def cors_response(request, response):
    hdr_val = request.headers.get('Origin')
    if hdr_val is not None:
        response.headers.add('Access-Control-Allow-Origin', hdr_val)
        response.headers.add('Access-Control-Allow-Credentials', 'true')

    req_headers = request.headers.get('Access-Control-Request-Headers')
    if req_headers is not None:
        response.headers.add('Access-Control-Allow-Headers', req_headers)

    req_method = request.headers.get('Access-Control-Request-Method')
    if req_method is not None:
        response.headers.add('Access-Control-Allow-Methods',
                             ','.join((req_method, 'OPTIONS')))

    return response


def can_modify_db(func):
    '''
        Decorator function to test if database modification is allowed.
    '''
    def wrapper_func(request):
        if request.registry.settings['caps.can_modify_db'].lower() == 'true':
            return func(request)
        else:
            raise HTTPForbidden('Access Forbidden')

    return wrapper_func
