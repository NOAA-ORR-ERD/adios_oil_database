from cornice import Service

from ..common.views import cors_policy


capabilities_api = Service(name='capabilities', path='/capabilities',
                           description=('List the capabilities of the '
                                        'oil database API'),
                           cors_policy=cors_policy)


@capabilities_api.get()
def get_capabilities(request):
    '''
        List the capabilities of the oil database API
    '''
    prefix = 'caps.'

    return dict([(s[len(prefix):], request.registry.settings[s])
                for s in request.registry.settings
                if s.startswith(prefix)])
