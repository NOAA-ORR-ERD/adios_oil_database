""" Cornice services.
"""
import re
import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound, HTTPNotImplemented

from pymodm.errors import DoesNotExist
from bson.errors import InvalidId

from ..common.views import cors_policy, obj_id_from_url

from oil_database.util.json import jsonify_oil_record

from oil_database.models.oil import Oil

from oil_database.models.common import Category
from oil_database.data_sources.oil import OilEstimation

logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oil*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


@oil_api.get()
def get_oils(request):
    '''
        We will do one of two possible things here.
        1. Return the searchable fields for all oils in JSON format.
        2. Return the JSON record of a particular oil.
    '''
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        res = get_oil_dict(obj_id)

        if res is not None:
            return res
        else:
            raise HTTPNotFound()
    else:
        return [get_oil_searchable_fields(o)
                for o in Oil.objects.all()]


@oil_api.post()
def insert_oil(request):
    raise HTTPNotImplemented


@oil_api.put()
def update_oil(request):
    raise HTTPNotImplemented


@oil_api.delete()
def delete_oil(request):
    raise HTTPNotImplemented


def get_oil_dict(obj_id):
    klass, query_set = Oil, {'_id': obj_id}

    try:
        result = klass.objects.get(query_set)
    except (DoesNotExist, InvalidId):
        return None

    if isinstance(result, klass):
        return jsonify_oil_record(result)
    elif len(result) > 0:
        return jsonify_oil_record(result[0])


def get_oil_non_embedded_docs(oil_dict):
    '''
        Custom routine to retrieve any non-embedded documents that are
        referenced by our oil attributes.

        Right now we are handling:
        - categories
    '''
    for i, c in enumerate(oil_dict['categories']):
        oil_dict['categories'][i] = (Category.objects.get({'_id': c})
                                     .to_son().to_dict())


def get_oil_searchable_fields(oil):
        oil_estimation = OilEstimation(oil)

        return {'oil_id': oil.oil_id,
                'name': oil.name,
                'location': oil.location,
                'product_type': oil.product_type,
                'apis': [a.to_son().to_dict() for a in oil.apis],
                'pour_point': oil_estimation.pour_point(),
                'viscosity': oil_estimation.kvis_at_temp(273.15 + 38),
                'categories': get_category_paths(oil),
                'categories_str': get_category_paths_str(oil),
                'status': oil.status,
                }


def get_category_paths_str(oil, sep=','):
    regex = re.compile(r'\b(Crude-|Refined-|Other-)\b')

    cat_str = sep.join(sorted(set(get_category_paths(oil))))

    return regex.sub("", cat_str)


def get_category_paths(oil, sep='-'):
    return [sep.join([c.name for c in get_category_ancestors(cat)])
            for cat in oil.categories]


def get_category_ancestors(category):
    '''
        Here we take a category, which is assumed to be a node
        in a tree structure, and determine the parents of the category
        all the way up to the apex.
    '''
    cat_list = []
    cat_list.append(category)

    while category.parent is not None:
        cat_list.append(category.parent)
        category = category.parent

    cat_list.reverse()
    return cat_list


def get_synonyms(oil, sep=','):
    syn_list = [s.name for s in oil.synonyms]

    return sep.join(syn_list)
