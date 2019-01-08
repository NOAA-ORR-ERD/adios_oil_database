from cornice import Service
from pyramid.httpexceptions import HTTPNotImplemented

from ..common.views import cors_policy


query_api = Service(name='query', path='/query',
                    description=('Query the oil database API'),
                    cors_policy=cors_policy)


@query_api.get()
def query_oils(request):
    '''
        Query the oil database API
    '''
    raise HTTPNotImplemented
