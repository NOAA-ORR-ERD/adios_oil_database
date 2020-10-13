import logging

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPUnsupportedMediaType)

from oil_database_api.common.views import cors_policy

from oil_database.models.oil.values import PRODUCT_TYPES


logger = logging.getLogger(__name__)

product_type_api = Service(name='product_types',
                           path='/product_types',
                           description="Endpoint for getting product types",
                           cors_policy=cors_policy)


@product_type_api.get()
def get_product_types(request):
    '''
    returns all the product types
    '''
    return PRODUCT_TYPES


# @label_api.post()
# def insert_labels(request):
#     try:
#         json_obj = ujson.loads(request.body)

#         # Since we are only expecting a dictionary struct here, let's raise
#         # an exception in any other case.
#         if not isinstance(json_obj, dict):
#             raise ValueError('JSON dict is the only acceptable payload')
#     except Exception as e:
#         raise HTTPBadRequest(e)

#     try:
#         # We don't have our data classes anymore so we need to inject
#         # at least a little bit of sanity here.  We will fail if we don't
#         # have at least these attributes.
#         required_attrs = ('name',)
#         if any([a not in json_obj for a in required_attrs]):
#             raise ValueError('Label insert objects must have at least '
#                              'these attributes: {}'
#                              .format(required_attrs))

#         if '_id' in json_obj:
#             json_obj['_id'] = ObjectId(json_obj['_id'])
#             print('insert_label(): requested _id: ', json_obj['_id'])

#         json_obj['_id'] = (request.mdb_client.oil_database.label
#                            .insert_one(json_obj)
#                            .inserted_id)
#         print('insert_label(): _id: ', json_obj['_id'])
#     except Exception as e:
#         raise HTTPUnsupportedMediaType(detail=e)

#     return fix_bson_ids(json_obj)

