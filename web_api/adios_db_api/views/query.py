import logging
import ujson

from cornice import Service

from pyramid.httpexceptions import HTTPBadRequest

from adios_db.util.json import jsonify_model_obj

from adios_db_api.common.views import (cors_policy,
                                       cors_exception)

log = logging.getLogger(__name__)

query_api = Service(name='query', path='/query',
                    description=('Oil Database Query API'),
                    cors_policy=cors_policy)


@query_api.post()
def query_oils(request):
    '''
        Query the oil database API

        We will use the builtin MongoDB querying syntax, based on JSON
    '''
    log_prefix = 'req({0}): query_oils():'.format(id(request))
    log.info('>> ' + log_prefix)

    try:
        json_request = ujson.loads(request.body)
    except Exception:
        raise cors_exception(request, HTTPBadRequest)

    db = request.mdb_client.adios_db

    table_name = json_request.get('table', 'oil')
    query = json_request.get('query', {})

    print("db:", db)
    print("collections", db.list_collection_names())

    if table_name in db.list_collection_names():
        collection = getattr(db, table_name)
    else:
        raise HTTPBadRequest('Invalid table name {}!'.format(table_name))

    log.info('<< ' + log_prefix)

    return [jsonify_model_obj(o) for o in list(collection.find(query))]
