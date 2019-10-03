# initialize mongodb connection after starting ipython
# just type: 'run ipy_init.py' after starting ipython
from pymongo import MongoClient

from oil_database.util.db_connection import connect_mongodb
from oil_database.data_sources.oil.estimations import OilEstimation

from oil_database.models.common.float_unit import DensityUnit, TemperatureUnit
from oil_database.models.common import Category
from oil_database.models.oil import Density

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

client = connect_mongodb({'mongodb.host': 'localhost',
                          'mongodb.port': 27017,
                          'mongodb.database': 'oil_database',
                          'mongodb.alias': 'oil-db-app'})

# ok, so we fail to import our PyMODM model classes
# if a connection hasn't been made yet.  Lame!!
from oil_database.models.noaa_fm import imported_rec
from oil_database.models.oil import Oil
from oil_database.models.common import Category

db = client.oil_database
records = db.imported_record
oils = db.oil
categories = db.category

print('categories.count_documents(): ', categories.count_documents({}))
print('categories.find_one(): ', categories.find_one())


my_cat = Category(name='Crude', db=db)
print('my_cat.dict():')
pp.pprint(my_cat.dict())

my_cat._id = categories.insert_one(my_cat.dict()).inserted_id
print('categories.find({})')
pp.pprint(list(categories.find({})))
print('my_cat.dict():')
pp.pprint(my_cat.dict())

child_cat = Category(name='Light', db=db)
print('child_cat.dict():')
pp.pprint(child_cat.dict())

child_cat._id = categories.insert_one(child_cat.dict()).inserted_id
print('categories.find({})')
pp.pprint(list(categories.find({})))
print('child_cat.dict():')
pp.pprint(child_cat.dict())

print('appending...')
my_cat.append(child_cat)
categories.replace_one({'_id': child_cat._id}, child_cat.dict(), upsert=True)
categories.replace_one({'_id': my_cat._id}, my_cat.dict(), upsert=True)

print('categories.find({})')
pp.pprint(list(categories.find({})))

