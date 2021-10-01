## Oil Database General Scripting Area

This is the general place we can put ad-hoc scripts which use the oil_database.

These are not intended to be installable via setup.py, but runable within the scope of this folder (Or elsewhere).
There is a scripts folder within the adios_db module for installable scripts.

This package provided various features for working with data in the ADIOS Oil Database. The data can be either in a collection fo JSON files, or in a MongoDB database for faster querying, etc.

### Working with the JSON data
The scripts in this dir are designed to work directly with the data in JSON files.

Most of them expect a command-line argument that points to the dir that holds the JSON files, such as what is found in the noaa-oil-data project.

### Example script

`example_query_script.py` is an example of searching the database for certain records and exporting specific data to a CSV file. It's a good starting point for how to work with the data.


### MongoDB scripts
Scripts that use the MongoDB are in the mongo_scripts dir

