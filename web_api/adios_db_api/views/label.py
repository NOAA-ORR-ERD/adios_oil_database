import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from bson.objectid import ObjectId
from bson.errors import InvalidId

from adios_db.util.json import fix_bson_ids

from adios_db_api.common.views import (cors_policy,
                                       obj_id_from_url,
                                       can_modify_db)


logger = logging.getLogger(__name__)

label_api = Service(name='label', path='/labels*obj_id',
                    description="Label APIs", cors_policy=cors_policy)


@label_api.get()
def get_labels(request):
    '''
        We will do one of two possible things here.
        1. Return all labels in JSON format.
        2. Return the JSON record of a particular label.
    '''
    obj_id = obj_id_from_url(request)

    try:
        res = request.mdb_client.get_labels(obj_id)
    except ValueError as e:
        raise HTTPBadRequest(e)

    if res is None:
        raise HTTPNotFound('label object not found')
    else:
        return res
