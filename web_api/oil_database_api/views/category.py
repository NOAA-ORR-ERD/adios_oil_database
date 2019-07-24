import logging

import ujson

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from pymodm.errors import DoesNotExist
from bson.objectid import ObjectId
from bson.errors import InvalidId

from oil_database.util.json import jsonify_model_obj
from oil_database.models.common import Category

from oil_database_api.common.views import cors_policy, obj_id_from_url


logger = logging.getLogger(__name__)

category_api = Service(name='category', path='/categories*obj_id',
                       description="Category APIs", cors_policy=cors_policy)


@category_api.get()
def get_categories(request):
    '''
        We will do one of two possible things here.
        1. Return all categories in JSON format.
        2. Return the JSON record of a particular category.
    '''
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        res = get_category_dict(obj_id)

        if res is not None:
            return res
        else:
            raise HTTPNotFound()
    else:
        return [get_category_dict(c._id) for c in Category.objects.all()]


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
        obj = Category(**json_obj)
        obj.save()
    except Exception as e:
        print e
        raise HTTPUnsupportedMediaType(detail=e)

    return jsonify_model_obj(obj)


@category_api.put()
def update_category(request):
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
        print('putting category object: {}'.format(json_obj))
        obj = Category(**json_obj)
        obj.save()
        print('put category success!!')
    except Exception as e:
        print e
        raise HTTPUnsupportedMediaType(detail=e)

    return jsonify_model_obj(obj)


@category_api.delete()
def delete_oil(request):
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        res = get_one_category(ObjectId(obj_id))

        if res is None:
            raise HTTPNotFound()
        else:
            # should maybe wrap this in a try, and return any failure response
            return res.delete()
    else:
        raise HTTPBadRequest


def get_one_category(obj_id):
    try:
        klass, query_set = Category, {'_id': ObjectId(obj_id)}
        result = klass.objects.get(query_set)
    except (DoesNotExist, InvalidId):
        return None

    if isinstance(result, klass):
        return result
    elif len(result) > 0:
        return result[0]


def get_category_dict(obj_id):
    return jsonify_model_obj(get_one_category(obj_id))
