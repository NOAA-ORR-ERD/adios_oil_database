import logging

from pymongo import MongoClient
from pymodm import connect
from pymodm.connection import _get_connection

logger = logging.getLogger(__name__)


def connect_mongodb(settings):
    '''
        We are using MongoDB via pymongo for our database
    '''
    host = settings['mongodb.host']
    port = settings['mongodb.port']

    return MongoClient(host=host, port=port)


def connect_modm(settings):
    '''
        We are using MongoDB via pymongo for our database, but we are using
        PyMODM to handle the object representations.  Here's why.

        PyMODM handles the definition and management of python storage objects
        similar to SQLAlchemy, which is much nicer to work with.  But...
        It does not directly use a client connection object.  The Model
        classes contain a Meta class that defines an 'alias' which identifies
        a connection to a particular MongoDB database.

        So you pymodm.connect() to a database, passing in an alias that
        matches the one referenced by your storage class's Meta values.  You
        don't even need to save a connection object for later.
        Then you simply instantiate your Model class objects and perform an
        obj.save() when you are ready to save them.
    '''
    host = settings['mongodb.host']
    port = settings['mongodb.port']
    db_name = settings['mongodb.database']
    connection_alias = settings['mongodb.alias']

    connect('mongodb://{}:{}/{}'.format(host, port, db_name), connection_alias)


def get_modm_connection(settings):
    alias = settings['mongodb.alias']
    return _get_connection(alias)
