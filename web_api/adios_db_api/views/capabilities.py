import logging

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest, HTTPNotFound)

from adios_db_api.common.views import (cors_policy, obj_id_from_url)

from adios_db import __version__ as __db_version__
from adios_db_api import __version__ as __web_api_version__

capabilities_api = Service(name='capabilities', path='/capabilities/*obj_id',
                           description=('List the capabilities of the '
                                        'oil database API'),
                           cors_policy=cors_policy)

logger = logging.getLogger(__name__)


@capabilities_api.get()
def get_capabilities(request):
    """
    List the capabilities of the oil database API
    """
    prefix = 'caps.'
    caps = dict([(s[len(prefix):], request.registry.settings[s])
                 for s in request.registry.settings
                 if s.startswith(prefix)])
    caps.update({'_id': 0,
                 'db_version': __db_version__,
                 'web_api_version': __web_api_version__})

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
