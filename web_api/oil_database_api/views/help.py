"""
Views for help documentation
"""
from os import walk
from os.path import sep, join, isfile, isdir

import time
import ujson
import urllib
import redis

from docutils.core import publish_parts

from cornice import Service
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from oil_database_api.common.views import cors_exception, cors_policy
from oil_database_api.common.indexing import iter_keywords


help_svc = Service(name='help', path='/help*dir',
                   description="Help Documentation and Feedback API",
                   cors_policy=cors_policy)


@help_svc.get()
def get_help(request):
    '''
        Get the requested help file if it exists
    '''
    help_dir = get_help_dir_from_config(request)
    requested_dir = urllib.parse.unquote(sep.join(request.matchdict['dir']))
    print('get_help(): help_dir: ', help_dir)
    print('get_help(): requested_dir: ', requested_dir)

    requested_file = join(help_dir, requested_dir)

    if isfile(requested_file + '.rst'):
        # a single help file was requested
        html = ''
        with open(requested_file + '.rst', 'r') as f:
            html = publish_parts(f.read(), writer_name='html')['html_body']

        return {'path': requested_file, 'html': html}
    elif isdir(requested_file) and requested_dir is not '':
        # a directory was requested
        # aggregate the files contained with in the given directory
        # and sub dirs.
        for path, _dirnames, filenames in walk(requested_file):
            html = ''
            for fname in filenames:
                with open(join(path, fname), 'r') as f:
                    html += publish_parts(f.read(),
                                          writer_name='html')['html_body']

            return {'path': requested_file, 'html': html}
    elif isdir(requested_file) and requested_dir is '':
        aggregate = []
        for path, _dirnames, filenames in walk(requested_file):
            for fname in filenames:
                text = ''
                with open(join(path, fname), 'r') as f:
                    text = f.read()

                parts_whole = publish_parts(text)
                parts = publish_parts(text, writer_name='html')

                html = parts['html_body']
                keywords = iter_keywords(parts_whole['whole'])

                aggregate.append({'path': join(path,
                                               fname.replace('.rst', '')),
                                  'html': html,
                                  'keywords': keywords})

        return aggregate
    else:
        raise cors_exception(request, HTTPNotFound)


@help_svc.put()
@help_svc.post()
def create_help_feedback(request):
    '''Creates a feedback entry for the given help section'''
    try:
        json_request = ujson.loads(request.body)
    except Exception:
        raise cors_exception(request, HTTPBadRequest)

    json_request['ts'] = int(time.time())

    # find redis using redis sessions config
    rhost = request.registry.settings.get('redis.sessions.host', 'localhost')
    rport = request.registry.settings.get('redis.sessions.port', 6379)

    client = redis.Redis(host=rhost, port=rport)

    if 'index' not in json_request:
        json_request['index'] = client.incr('index')

    client.set('feedback' + str(json_request['index']),
               str(json_request))

    return json_request


def get_help_dir_from_config(request):
    '''
        Here we try to make the configs flexible enough to reasonably handle
        absolute & relative paths.
        - install path should be an absolute path
        - help_dir can be an absolute or relative path.  If relative, we will
          prepend the install_dir.  (builtin join method should handle this)
    '''
    here = request.registry.settings['install_path']
    help_dir = request.registry.settings['help_dir']

    full_path = join(here, help_dir)

    return full_path
