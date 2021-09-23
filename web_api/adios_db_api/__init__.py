"""
Main entry point
"""
import os
import datetime

import json

from adios_db.session import Session

from pyramid.config import Configurator
from pyramid.response import Response, FileResponse
from pyramid.renderers import JSON as JSONRenderer

from .common.views import cors_policy

__version__ = "0.2.1"


def load_cors_origins(settings, key):
    print("loading cors policy", key)
    if key in settings:
        try:
            origins = settings[key].split('\n')
        except AttributeError:  # Assume it's already a list
            origins = settings[key]
        cors_policy['origins'] = [s.strip() for s in origins]
    print("cors_policy set:")
    print(cors_policy['origins'])


def attach_pymongo(config, settings):
    host = settings['mongodb.host'].strip()
    port = int(settings['mongodb.port'])
    db_name = settings['mongodb.database']

    # build mongo client and attach to request registry
    config.registry.db = Session(host=host, port=port, database=db_name)

    # add request method
    def add_db(_request):
        return config.registry.db

    config.add_request_method(add_db, 'mdb_client', reify=True)


def get_json(request):
    return json.loads(request.text, ensure_ascii=False)


def about(_request):
    """
        A simple view that give a little hello message if you hit the server
        directly
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


def default_not_found_response(_request):
    msg = '''
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <title>404 Not Found</title>
          </head>
          <body>
            <h1>404 Not Found</h1>

            The resource could not be found.<br>
            <br>
          </body>
        </html>
    '''
    return Response(msg, status='404 Not Found')


def json_datetime_part(o):
    '''
        This is only necessary if we are using the builtin json module
        ujson and orjson have no problems with datetime content.
    '''
    if isinstance(o, datetime.datetime):
        return o.isoformat()


def main(_global_config, **settings):

    print("*****running main of API****")
    load_cors_origins(settings, 'cors_policy.origins')

    config = Configurator(settings=settings)

    attach_pymongo(config, settings)

    config.add_request_method(get_json, 'json', reify=True)
    renderer = JSONRenderer(
        serializer=lambda v, **_kw: json.dumps(v, default=json_datetime_part,
                                               sort_keys=True, indent=4)
    )

    config.add_renderer('json', renderer)

    config.include("cornice")
    # config.scan("adios_db_api.views")

    # Attempt to set up the rest by hand -- scanning is not working when
    # bundled by py2app
    print("adding all the API rest services")
    from .views import oil
    config.add_cornice_service(oil.oil_api)

    from .views.label import label_api
    config.add_cornice_service(label_api)

    from .views.product_types import product_types_api
    config.add_cornice_service(product_types_api)

    from .views.capabilities import capabilities_api
    config.add_cornice_service(capabilities_api)

    # from .views.query import query_api
    # config.add_cornice_service(query_api)

    # add static file serving if we are running the standalone
    client_path = settings.get('client_path')
    if client_path:
        print("adding client code to serve:\n", client_path)
        if not os.path.isdir(client_path):
            raise ValueError(f"client path: {client_path} does not exist")

        # this would be cleaner, but couldn't get it to work with Ember
        config.add_static_view(name='/', path=client_path)

        # mike's suggestion for how to serve up the index.html page
        print("about to set up home view")

        def home(request):
            """serving up index.html"""
            return FileResponse(client_path + "/index.html", request)

        # this way has not been tested.
        config.add_route("home", "/")
        config.add_view(home, route_name="home")

        # attempt to put the client files in a sub-dir
        #  to avoid clashes with the API
        # config.add_static_view(name='client',
        #                        path=client_path)

    else:
        # serve up the basic hello message at the root
        print("no client_path: not serving any static files")
        config.add_route('home', '/')
        config.add_view(about, route_name='home')

    # setup the about endpoint
    config.add_route('about', '/about')
    config.add_view(about, route_name='about')
    config.add_notfound_view(default_not_found_response, append_slash=True)

    return config.make_wsgi_app()
