## ADIOS Oil Database: scrips for working with Mongo


To start out, we will need to connect to the oil database.  This requires a
.ini file with the appropriate settings to connect to the database we are
interested in.

*settings_default.ini*

    [app:adios_db]
    use = egg:adios_db

    mongodb.host = localhost
    mongodb.port = 27017
    mongodb.database = adios_db
    mongodb.alias = adios-db-app

This example will configure a connection to a mongodb database at its default
port on the local machine, and use a database named 'adios_db'.

We can now start to write Python scripts that use these settings.  The first
thing to do is instantiate a session with mongodb:

    from adios_db.util.settings import file_settings
    from adios_db.util.db_connection import connect_mongodb

    settings = file_settings('settings_default.ini')

    session = connect_mongodb(settings)
    #session2 = connect_mongodb(settings2)  # we can start multiple sessions if needed

