import logging

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound)

from adios_db_api.common.views import (cors_policy,
                                       cors_response,
                                       obj_id_from_url)


capabilities_api = Service(name='capabilities', path='/capabilities/*obj_id',
                           description=('List the capabilities of the '
                                        'oil database API'),
                           cors_policy=cors_policy)

logger = logging.getLogger(__name__)


@capabilities_api.get()
def get_capabilities(request):
    '''
        List the capabilities of the oil database API
    '''
    prefix = 'caps.'
    caps = dict([(s[len(prefix):], request.registry.settings[s])
                 for s in request.registry.settings
                 if s.startswith(prefix)])
    caps.update({'_id': 0})

    obj_id = obj_id_from_url(request)

    if obj_id is not None:
        try:
            obj_id = int(obj_id)
        except TypeError as e:
            logger.error(e)
            raise HTTPBadRequest()

        if obj_id != 0:
            raise HTTPNotFound()

        return caps
    else:
        return [caps]
