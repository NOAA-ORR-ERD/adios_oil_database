# initialize mongodb connection after starting ipython
# just type: 'run ipy_init.py' after starting ipython
from pymongo import MongoClient
from pymodm.fields import EmbeddedDocumentListField

from oil_database.util.db_connection import connect_modm
from oil_database.data_sources.oil.estimations import OilEstimation

from oil_database.models.common.float_unit import DensityUnit, TemperatureUnit
from oil_database.models.oil import Density

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

client = MongoClient()

connect_modm({'mongodb.host':'localhost',
              'mongodb.port':27017,
              'mongodb.database':'oil_database',
              'mongodb.alias':'oil-db-app'})

# ok, so we fail to import our PyMODM model classes
# if a connection hasn't been made yet.  Lame!!
from oil_database.models.noaa_fm import imported_rec
from oil_database.models.oil import Oil
from oil_database.models.common import Category

db = client.oil_database
records = db.imported_record
oils = db.oil

print(Oil.objects.first())

for oil_obj in Oil.objects.raw({'product_type': 'crude'}):
    oil_view = OilEstimation(oil_obj)

    print('\n', oil_view.record.oil_id, oil_view.record.name)
    print('\t', oil_view.pour_point())













