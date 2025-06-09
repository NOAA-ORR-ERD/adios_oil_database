# Oil Database Management Package

This is a Python package for managing a collection of records about oil used
for oil spill response.

The records conform to the NOAA "Response Oil Assay" data model, and can be loaded and saved from/to a custom JSON format, as well as imported from a handful of other specialized formats.

This library can be used for importing data from arbitrary formats by writing a custom importer.

The entire dataset can be managed in MongoDB, a popular object database system, but that is unnecessary, unless you want to run a web application, such as NOAA's ADIOS Oil Database:

## Where to find data

The collection of oil records that NOAA maintains is found on gitHub here:

https://github.com/NOAA-ORR-ERD/noaa-oil-data

That is a collection of JSON files, one for each record. This package is essentially a tool for manipulating that data.

Anyone, or course could maintain their own collection of data.

## Documentation:

The documentation for this package is in this repo in `adios_db/Documentation/API_docs/` as a Sphinx doc, and published at:

https://noaa-orr-erd.github.io/adios_oil_database/


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

The `adios_db` package is available on conda-forge:

https://anaconda.org/conda-forge/adios_db

Or can be installed from source:

(source at: https://github.com/NOAA-ORR-ERD/adios_oil_database)

```
cd adios_db  # if you haven't already

python -m pip install .

or, of you ware working on the code, and editable install:

python -m pip install -e .
```

This will install the Python package, which can then be used with:

`import adios_db`

If installing from source, you will need the requirements in:

`conda_requirements.txt`

(these should all be pip-installable as well)





