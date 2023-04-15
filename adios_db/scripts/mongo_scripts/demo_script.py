# mockup of what we would like in order to separate
# the mongodb API from our code
from pprint import pprint

from adios_db.util.db_connection import connect_mongodb
from adios_db.util.settings import file_settings


# The session will be an instance of our oil_db session object, not mongodb
# our session is already connected to the database specified in settings
# We will be able to construct multiple session objects, each one connected to
# a mongodb database
settings = file_settings('settings_default.ini')
session = connect_mongodb(settings)


# The general purpose query function (this will be very verbose)
print('Query by id...')
print('Return only the name & location fields...')
for rec in session.query(oil_id='AD00020',
                         projection=['metadata.name',
                                     'metadata.location']):
    pprint(rec)


print('\n\nQuery by name and location, inclusive and case-sensitive.')
print('Return only the name & location fields...')
for idx, rec in enumerate(session.query(text='Alaska North Slope',
                                        projection=['metadata.name',
                                                    'metadata.location'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by labels = ["Crude", "Medium"]')
print('Return only the name & labels fields...')
for idx, rec in enumerate(session.query(labels=['Crude', 'Medium'],
                                        projection=['metadata.name',
                                                    'metadata.labels'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by labels = "Crude,Medium"]')
print('Return only the name & labels fields...')
for idx, rec in enumerate(session.query(labels='Crude,Medium',
                                        projection=['metadata.name',
                                                    'metadata.labels'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by labels = "Crude, Medium"]')
print('Return only the name & labels fields...')
for idx, rec in enumerate(session.query(labels='Crude, Medium',
                                        projection=['metadata.name',
                                                    'metadata.labels'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = 50')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api=50,
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = [50]')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api=[50],
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = [None, 10]')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api=[None, 10],
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = [10, 15]')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api=[10, 15],
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = "10,15"')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api='10,15',
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = "10, 15"')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api='10, 15',
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')


print('\n\nQuery by api = [15, 10]')
print('Return only the name & API fields...')
for idx, rec in enumerate(session.query(api=[15, 10],
                                        projection=['metadata.name',
                                                    'metadata.API'])):
    pprint(f'{idx}: {rec}')
