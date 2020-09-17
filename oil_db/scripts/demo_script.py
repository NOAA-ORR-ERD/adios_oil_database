# mockup of what we would like in order to separate
# the mongodb API from our code
from oil_database.util.db_connection import connect_mongodb
from oil_database.util.settings import file_settings
from pprint import pprint


# The session will be an instance of our oil_db session object, not mongodb
# our session is already connected to the database specified in settings
# We will be able to construct multiple session objects, each one connected to
# a mongodb database
settings = file_settings('settings_default.ini')

session = connect_mongodb(settings)
#session2 = connect_mongodb(settings2)


# The general purpose query function (this will be very verbose)
print('Open query...')
for rec in session.query():
    pprint(rec)

print('Query by id...')
for rec in session.query(id='AD00020'):
    pprint(rec)


print('\n\nQuery by name and location, inclusive and case-sensitive.')
print('Return only the name & location fields...')
for idx, rec in enumerate(session.query(name='Alaska North Slope',
                                        location='Alaska North Slope',
                                        projection=['metadata.name',
                                                    'metadata.location'],
                                        ignore_case=False, inclusive=True)):
    pprint(f'{idx}: {rec}')
