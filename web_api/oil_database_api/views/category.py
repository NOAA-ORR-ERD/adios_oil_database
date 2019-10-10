import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from bson.objectid import ObjectId
from bson.errors import InvalidId

from oil_database.util.json import fix_bson_ids

from oil_database_api.common.views import cors_policy, obj_id_from_url


logger = logging.getLogger(__name__)

category_api = Service(name='category', path='/category*obj_id',
                       description="Category APIs", cors_policy=cors_policy)


@category_api.get()
def get_categories(request):
    '''
        We will do one of two possible things here.
        1. Return all categories in JSON format.
        2. Return the JSON record of a particular category.
    '''
    obj_id = obj_id_from_url(request)
    categories = request.db.oil_database.category

    if obj_id is not None:
        try:
            res = categories.find_one({'_id': ObjectId(obj_id)})
        except InvalidId as e:
            raise HTTPBadRequest(e)

        if res is not None:
            print('res: ', res)
            return fix_bson_ids(res)
        else:
            raise HTTPNotFound()
    else:
        return fix_bson_ids(list(categories.find({})))


@category_api.post()
def insert_category(request):
    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception as e:
        raise HTTPBadRequest(e)

    try:
        # We don't have our data classes anymore so we need to inject
        # at least a little bit of sanity here.  We will fail if we don't
        # have at least these attributes.
        required_attrs = ('name',)
        if any([a not in json_obj for a in required_attrs]):
            raise ValueError('Category insert objects must have at least '
                             'these attributes: {}'
                             .format(required_attrs))

        if '_id' in json_obj:
            json_obj['_id'] = ObjectId(json_obj['_id'])
            print('insert_category(): requested _id: ', json_obj['_id'])

        json_obj['_id'] = (request.db.oil_database.category
                           .insert_one(json_obj)
                           .inserted_id)
        print('insert_category(): _id: ', json_obj['_id'])
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return fix_bson_ids(json_obj)


@category_api.put()
def update_category(request):
    try:
        json_obj = ujson.loads(request.body)

        # Since we are only expecting a dictionary struct here, let's raise
        # an exception in any other case.
        if not isinstance(json_obj, dict):
            raise ValueError('JSON dict is the only acceptable payload')
    except Exception:
        raise HTTPBadRequest

    try:
        print('putting category object: {}'.format(json_obj))

        # We will fail if we don't have at least these attributes.
        required_attrs = ('_id', 'name',)
        if any([a not in json_obj for a in required_attrs]):
            raise ValueError('Category update objects must have at least '
                             'these attributes: {}'
                             .format(required_attrs))

        json_obj['_id'] = ObjectId(json_obj['_id'])
        print('update_category(): _id: ', json_obj['_id'])

        (request.db.oil_database.category
         .replace_one({'_id': json_obj['_id']}, json_obj))

        print('put category success!!')
    except Exception as e:
        raise HTTPUnsupportedMediaType(detail=e)

    return fix_bson_ids(json_obj)


@category_api.delete()
def delete_category(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        obj_id = ObjectId(obj_id)
        print('delete_category(): _id: ', obj_id)

        res = (request.db.oil_database.category
               .delete_one({'_id': obj_id}))

        if res.deleted_count == 0:
            raise HTTPNotFound()

        return res
    else:
        raise HTTPBadRequest
