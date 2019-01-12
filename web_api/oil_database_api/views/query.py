import logging
import ujson

from cornice import Service

from pyramid.httpexceptions import HTTPBadRequest

from oil_database.util.db_connection import get_modm_connection
from oil_database.util.json import jsonify_oil_record

from ..common.views import (cors_policy,
                            cors_exception)

log = logging.getLogger(__name__)

query_api = Service(name='query', path='/query',
                    description=('Query the oil database API'),
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

    db = get_modm_connection(request.registry.settings).database
    table_name = json_request.get('table', 'oil')
    query = json_request.get('query', {})

    if table_name in db.collection_names():
        collection = getattr(db, table_name)
    else:
        raise HTTPBadRequest('Invalid table name!')

    log.info('<< ' + log_prefix)
    return [jsonify_oil_record(o) for o in list(collection.find(query))]
