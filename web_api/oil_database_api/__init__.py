"""
Main entry point
"""
import logging

import ujson

from pyramid.config import Configurator
from pyramid.renderers import JSON as JSONRenderer

from oil_database.util.db_connection import connect_mongodb

from .common.views import cors_policy


def load_cors_origins(settings, key):
    if key in settings:
        origins = settings[key].split('\n')
        cors_policy['origins'] = origins


def generate_mongodb2_settings(settings):
    '''
        These settings are required by pyramid_mongodb2.
        We build them from our original settings.

        An example mongo URI is:
            mongodb://username:password@mongodb.host.com:27017/authdb

        But we don't use all the options for connecting (yet)
    '''
    host = settings['mongodb.host'].strip()
    port = settings['mongodb.port'].strip()
    db_name = settings['mongodb.database']

    mongo_uri = 'mongodb://{}:{}'.format(host, port)

    settings['mongo_uri'] = mongo_uri
    settings['mongo_dbs'] = db_name


def get_json(request):
    return ujson.loads(request.text, ensure_ascii=False)


def main(global_config, **settings):

    print("in main: global_config:")
    print(global_config)

    print("in main: settings:")
    print(settings)

    load_cors_origins(settings, 'cors_policy.origins')
    generate_mongodb2_settings(settings)

    config = Configurator(settings=settings)

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)

    config.include("cornice")
    config.scan("oil_database_api.views")

    return config.make_wsgi_app()
