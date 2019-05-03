""" Cornice services.
"""
import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound, HTTPNotImplemented

from pymodm.errors import DoesNotExist
from bson.errors import InvalidId

from ..common.views import cors_policy, obj_id_from_url

from oil_database.util.json import jsonify_oil_record

from oil_database.models.ec_imported_rec import ECImportedRecord
from oil_database.models.common import Category

logger = logging.getLogger(__name__)

ec_record_api = Service(name='ec_record',
                        path='/ec_record*obj_id',
                        description=('List all Environment Canada '
                                     'imported records'),
                        cors_policy=cors_policy)


@ec_record_api.get()
def get_imported_records(request):
    '''
        We will do one of two possible things here.
        1. Return the searchable fields for all Environment Canada records
           in JSON format.
        2. Return the JSON record of a particular Environment Canada record.
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
                for o in ECImportedRecord.objects.all()]


@ec_record_api.post()
def insert_imported_record(request):
    raise HTTPNotImplemented


@ec_record_api.put()
def update_imported_record(request):
    raise HTTPNotImplemented


@ec_record_api.delete()
def delete_imported_record(request):
    raise HTTPNotImplemented


def get_imported_record_dict(obj_id):
    klass, query_set = ECImportedRecord, {'oil_id': obj_id}

    try:
        result = klass.objects.get(query_set)
    except (DoesNotExist, InvalidId):
        return None

    if isinstance(result, klass):
        return jsonify_oil_record(result)
    else:
        return jsonify_oil_record(result[0])


def get_imported_record_non_embedded_docs(oil_dict):
    '''
        Custom routine to retrieve any non-embedded documents that are
        referenced by our oil attributes.

        Right now we are handling:
        - categories
    '''
    for i, c in enumerate(oil_dict['categories']):
        oil_dict['categories'][i] = (Category.objects.get({'_id': c})
                                     .to_son().to_dict())


def get_imported_record_searchable_fields(oil):
    '''
        Not entirely sure what the searchable fields should be for the
        Environment Canada records, but we will come up with a short list here.
    '''
    return {'oil_id': oil.oil_id,
            'name': oil.oil_name,
            'location': oil.location,
            'product_type': oil.product_type,
            'api': oil.api,
            'pour_point': get_pour_point(oil),
            'synonyms': get_synonyms(oil),
            }


def get_synonyms(oil, sep=','):
    syn_list = [s.name for s in oil.synonyms]

    return sep.join(syn_list)


def get_pour_point(oil):
    return oil.pour_points







