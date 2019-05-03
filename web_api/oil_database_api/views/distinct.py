""" Cornice services.
"""
from collections import defaultdict

from cornice import Service

from ..common.views import cors_policy

from oil_database.models.noaa_fm import ImportedRecord
from oil_database.models.common import Category

distinct_api = Service(name='distinct', path='/distinct',
                       description=('List the distinct values of the '
                                    'searchable fields in the Oil database'),
                       cors_policy=cors_policy)


@distinct_api.get()
def get_distinct(request):
    '''
        Queries all oils, compiling lists of distinct values for specified
        attributes.

        TODO: Maybe we should specify the distinct attributes we would like
              in the request.GET arguments.
    '''
    res = defaultdict(set)

    attrs = ('location',
             'field_name')

    for ir_attrs in ImportedRecord.objects.only(*attrs):
        for a in attrs:
            res[a].add(getattr(ir_attrs, a))

    # Categories are in a slightly different format than the rest, so we
    # handle them separately.
    category_dict = {}
    for parent in Category.objects.raw({'parent': None}):
        category_dict.update(child_categories(parent))

    return ([dict(column=k, values=sorted(v)) for k, v in res.iteritems()] +
            [dict(column='product_type', values=category_dict)])


def child_categories(category):
    '''
        This is a recursive method to return a tree of sub-categories
    '''
    name = category.name
    if category.children is not None and len(category.children) > 0:
        return {name: [child_categories(c) for c in category.children]}
    else:
        return name
