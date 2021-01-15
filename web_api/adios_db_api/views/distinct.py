""" Cornice services.
"""
from collections import defaultdict

from cornice import Service

from adios_db_api.common.views import cors_policy

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

    attrs = ('location',)

    oils = request.db.adios_db.oil
    categories = request.db.adios_db.category

    for ir_attrs in oils.find({}, projection=attrs + ('categories',)):
        for a in attrs:
            if ir_attrs[a] is not None:
                res[a].add(ir_attrs[a])

        categories = ir_attrs['categories']
        if categories is not None:
            for c in ir_attrs['categories']:
                res['product_type'].add(c)

    return [dict(column=k, values=sorted(v)) for k, v in res.items()]
