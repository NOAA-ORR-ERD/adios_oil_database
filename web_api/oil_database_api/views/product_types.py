import logging

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound)

from oil_database_api.common.views import cors_policy, obj_id_from_url

from oil_database.models.oil.product_type import PRODUCT_TYPES


logger = logging.getLogger(__name__)

product_types_api = Service(name='product-types',
                            path='/product-types*obj_id',
                            description="Endpoint for getting product types",
                            cors_policy=cors_policy)


@product_types_api.get()
def get_product_types(request):
    '''
    returns all the product types
    '''
    obj_id = obj_id_from_url(request)
    product_types = [{'name': p, '_id': i}
                     for i, p in enumerate(sorted(PRODUCT_TYPES))]

    if obj_id is not None:
        try:
            obj_id = int(obj_id)
        except TypeError as e:
            raise HTTPBadRequest(e)

        matches = [p for p in product_types if p['_id'] == obj_id]

        if len(matches) >= 1:
            return matches[0]
        else:
            print((obj_id,))
            raise HTTPNotFound()
    else:
        return product_types
