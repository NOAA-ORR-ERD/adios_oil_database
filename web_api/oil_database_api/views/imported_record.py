""" Cornice services.
"""
import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound, HTTPNotImplemented

from pymodm.errors import DoesNotExist
from bson.errors import InvalidId

from oil_database.util.json import jsonify_model_obj
from oil_database_api.common.views import cors_policy, obj_id_from_url

from oil_database.models.noaa_fm import ImportedRecord

logger = logging.getLogger(__name__)

imported_record_api = Service(name='imported_record',
                              path='/imported_record*obj_id',
                              description="List all imported records",
                              cors_policy=cors_policy)


@imported_record_api.get()
def get_imported_records(request):
    '''
        We will do one of two possible things here.
        1. Return the searchable fields for all imported records in JSON
           format.
        2. Return the JSON record of a particular imported record.
    '''
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        res = get_imported_record_dict(obj_id)

        if res is not None:
            return res
        else:
            raise HTTPNotFound()
    else:
        return [get_imported_record_searchable_fields(o)
                for o in ImportedRecord.objects.all()]


@imported_record_api.post()
def insert_imported_record(request):
    raise HTTPNotImplemented


@imported_record_api.put()
def update_imported_record(request):
    raise HTTPNotImplemented


@imported_record_api.delete()
def delete_imported_record(request):
    raise HTTPNotImplemented


def get_imported_record_dict(obj_id):
    klass, query_set = ImportedRecord, {'adios_oil_id': obj_id}

    try:
        result = klass.objects.get(query_set)
    except (DoesNotExist, InvalidId):
        return None

    if isinstance(result, klass):
        return jsonify_model_obj(result)
    else:
        return jsonify_model_obj(result[0])


def get_imported_record_searchable_fields(oil):
        return {'adios_oil_id': oil.adios_oil_id,
                'name': oil.oil_name,
                'location': oil.location,
                'field_name': oil.field_name,
                'product_type': oil.product_type,
                'oil_class': oil.oil_class,
                'api': oil.api,
                'pour_point': get_pour_point(oil),
                'synonyms': get_synonyms(oil),
                }


def get_synonyms(oil, sep=','):
    syn_list = [s.name for s in oil.synonyms]

    return sep.join(syn_list)


def get_pour_point(oil):
    return [oil.pour_point_min_k, oil.pour_point_max_k]
