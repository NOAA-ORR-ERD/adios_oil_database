# Oil Database Management Package

This is a Python package for managing a collection of records about oil used
for oil spill response.

The records conform to the NOAA "Response Oil Assay" data model, and can be loaded and saved from/to a custom JSON format, as well as imported from a handful of other specialized formats.

This library can be used for importing data from arbitrary formats by writing a custom importer.

The entire dataset can be managed in MongoDB, a popular object database system.


## Command Line Scripts

A couple of command-line applications are delivered along with this package.

#### `oil_db_init`

This is a command-line application that initializes the database.

```

$ oil_db_init --help
usage: oil_db_init [-h] [--config CONFIG]

Database Initialization Arguments:

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Specify a *.ini file to supply application settings. If not
                   specified, the default is to use a local MongoDB server.

```

#### `oil_db_import`

This is a command-line application that imports a number of oil record
data sets into the database.

```
$ oil_db_import --help
usage: oil_db_import [-h] [--all] [--config CONFIG]

Database Import Arguments:

optional arguments:
  -h, --help       show this help message and exit
  --all            Import all datasets, bypassing the menus, and quit the
                   application when finished.
  --config CONFIG  Specify a *.ini file to supply application settings. If not
                   specified, the default is to use a local MongoDB server.
```

## Installation

### For Deployment

#### Install the package

`pip install .`

This will install the Python package, which can then be used with:

`import oil_database`

#### Set up the Database

If you want to work with the data in MongoDB, you need to set up the mongo database:

`oil_db_init`

If you want to import fresh data from the delivered data sources:

`oil_db_import --all`


### For Development

For development, you may need to clean out the install, and want to install in "develop" or "editable" mode.

```
python setup.py clean
pip uninstall adios_db
pip install -e ./
oil_db_init
# optionally:
oil_db_import --all
```

NOTE: in order to initialize the database, you need an instance of MongoDB running.




