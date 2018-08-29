""" Cornice services.
"""
import re
import logging

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound

from pymodm.errors import DoesNotExist
from bson.errors import InvalidId

from ..common.views import cors_policy, obj_id_from_url

from oil_database.util.json import fix_bson_ids
from oil_database.models.oil import Oil
from oil_database.models.oil_props import OilProps
from oil_database.models.category import Category

logger = logging.getLogger(__name__)

oil_api = Service(name='oil', path='/oil*obj_id',
                  description="List All Oils", cors_policy=cors_policy)


def memoize_oil_arg(func):
    res = {}

    def memoized_func(oil):
        if oil.adios_oil_id not in res:
            res[oil.adios_oil_id] = func(oil)

        return res[oil.adios_oil_id]

    return memoized_func


@oil_api.get()
def get_oils(request):
    '''
        Return the searchable fields for all oils in JSON format.
    '''
    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        try:
            return get_oil_dict({'adios_oil_id': obj_id})
        except DoesNotExist:
            raise HTTPNotFound()
    elif len(request.GET) > 0:
        try:
            return get_oil_dict(dict(request.GET))
        except (DoesNotExist, InvalidId):
            raise HTTPNotFound()
    else:
        return [get_oil_searchable_fields(o) for o in Oil.objects.all()]


def get_oil_dict(query_set):
    # We will let the caller handle any exceptions
    oil = Oil.objects.get(query_set)
    oil_dict = oil.to_son().to_dict()

    get_oil_non_embedded_docs(oil_dict)

    fix_bson_ids(oil_dict)

    return oil_dict


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


@memoize_oil_arg
def get_oil_searchable_fields(oil):
        return {'adios_oil_id': oil.adios_oil_id,
                'name': oil.name,
                'location': oil.imported.location,
                'field_name': oil.imported.field_name,
                'product_type': oil.imported.product_type,
                'oil_class': oil.imported.oil_class,
                'api': oil.api,
                'pour_point': get_pour_point(oil),
                'viscosity': get_oil_viscosity(oil),
                'categories': get_category_paths(oil),
                'categories_str': get_category_paths_str(oil),
                'synonyms': get_synonyms(oil),
                'quality_index': oil.quality_index
                }


def get_category_paths_str(oil, sep=','):
    regex = re.compile(r'\b(Crude-|Refined-)\b')

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
    syn_list = [s.name for s in oil.imported.synonyms]

    return sep.join(syn_list)


def get_pour_point(oil):
    return [oil.pour_point_min_k, oil.pour_point_max_k]


def get_oil_viscosity(oil):
    if oil.api >= 0 and len(oil.kvis) > 0:
        oil_props = OilProps(oil)
        return oil_props.kvis_at_temp(273.15 + 38)
    else:
        return None
