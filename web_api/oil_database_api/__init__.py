"""Main entry point
"""
import logging

import ujson
from pyramid.config import Configurator
from pyramid.renderers import JSON as JSONRenderer

from oil_database.util.db_connection import connect_modm

from common.views import cors_policy


def load_cors_origins(settings, key):
    if key in settings:
        origins = settings[key].split('\n')
        cors_policy['origins'] = origins


def get_json(request):
    return ujson.loads(request.text, ensure_ascii=False)


def main(global_config, **settings):

    load_cors_origins(settings, 'cors_policy.origins')

    config = Configurator(settings=settings)
    connect_modm(settings)

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)

    config.include("cornice")
    config.scan("oil_database_api.views")

    return config.make_wsgi_app()
