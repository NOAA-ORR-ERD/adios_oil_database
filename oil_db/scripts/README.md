## Oil Database General Scripting Area

This is the general place we can put ad-hoc scripts which use the oil_database.

These are not intended to be installable via setup.py, but runnable within
the scope of this folder.  There is a scripts folder within the oil_database
module for installable scripts.

To start out, we will need to connect to the oil database.  This requires a
.ini file with the appropriate settings to connect to the database we are
interested in.

*settings_default.ini*

    [app:oil_database]
    use = egg:oil_database
    
    mongodb.host = localhost
    mongodb.port = 27017
    mongodb.database = oil_database
    mongodb.alias = oil-db-app

This example will configure a connection to a mongodb database at its default
port on the local machine, and use a database named 'oil_database'.

We can now start to write Python scripts that use these settings.  The first
thing to do is instantiate a session with mongodb:

    from oil_database.util.settings import file_settings
    from oil_database.util.db_connection import connect_mongodb
    
    settings = file_settings('settings_default.ini')
    
    session = connect_mongodb(settings)
    #session2 = connect_mongodb(settings2)  # we can start multiple sessions if needed

