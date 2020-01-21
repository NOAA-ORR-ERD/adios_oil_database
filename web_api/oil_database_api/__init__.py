"""
Main entry point
"""
import os

import ujson

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.renderers import JSON as JSONRenderer

# from oil_database.util.db_connection import connect_mongodb

from .common.views import cors_policy


def load_cors_origins(settings, key):
    if key in settings:
        try:
            origins = settings[key].split('\n')
        except AttributeError:  # Assume it's already a list
            origins = settings[key]
        cors_policy['origins'] = [s.strip() for s in origins]


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


def about(request):
    """
    A simple view that give a little hello message if you hit the server directly
    print('Incoming request')
    """
    msg = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>NOAA ADIOS Oil Database</title>
      </head>
      <body>
        <h1> NOAA ADIOS Oil Database </h1>
        <p>
            Welcome to the ADIOS oil database server.

            This service is a JSON Web REST Service.
        </p>
        <p>
            [We need to document the API here -- or point to docs.]
        </p>
      </body>
</html>
    """
    return Response(msg)


def main(global_config, **settings):

    load_cors_origins(settings, 'cors_policy.origins')
    generate_mongodb2_settings(settings)

    config = Configurator(settings=settings)

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(serializer=lambda v, **kw: ujson.dumps(v))
    config.add_renderer('json', renderer)

    config.include("cornice")
    config.scan("oil_database_api.views")

    # add static file serving if we are running the standalone
    client_path = settings.get('client_path')
    if client_path:
        print("adding client code to serve:\n", client_path)
        if not os.path.isdir(client_path):
            raise ValueError(f"client path: {client_path} does not exist")
        config.add_static_view(name='/',
                               path=client_path)
        # config.add_static_view(name='/client/',
        #                        path=client_path)

    else:
        # serve up the basic hello message at the root
        print("no client_path: not serving any static files")
        config.add_route('home', '/')
        config.add_view(about, route_name='home')
    # setup the about endpoint
    config.add_route('about', '/about')
    config.add_view(about, route_name='about')

    return config.make_wsgi_app()
