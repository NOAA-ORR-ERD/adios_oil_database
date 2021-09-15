""" Cornice services.
"""

# Fixme: is this required for anything

import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from bson.objectid import ObjectId


from adios_db_api.common.views import cors_policy, obj_id_from_url
from adios_db_api.util import fix_bson_ids

logger = logging.getLogger(__name__)

object_api = Service(name='object', path='/object/*obj_id',
                     description="Get an object by ID",
                     cors_policy=cors_policy)


@object_api.get()
def get_object(request):
    '''
        Get an object by its ID.  It can exist in any of the collections
        that are defined in the database.
    '''
    obj_id = obj_id_from_url(request)

    if obj_id is None:
        obj_id = request.GET.get('id', None)

    if obj_id is None:
        raise HTTPBadRequest('Object ID required')
    else:
        db = request.mdb_client.db

        try:
            obj_id = ObjectId(obj_id)
        except Exception:
            pass  # just use the obj_id as-is

        for cname in db.collection_names():
            collection = getattr(db, cname)

            obj = collection.find_one({'_id': obj_id})

            if obj is None:
                continue
            else:
                return fix_bson_ids(obj)

        raise HTTPNotFound()
