# Oil Database Management Package

This is a Python package for managing a collection of records about oil used
for oil spill response.

The records conform to the NOAA ADIOS® Oil Database Data Model, and can be loaded and saved from/to a custom JSON format, as well as imported from a handful of other specialized formats.

This library can be used for importing data from arbitrary formats by writing a custom importer.

The entire dataset can be managed in MongoDB, a popular object database system, but that is unnecessary, unless you want to run a web application, such as NOAA's ADIOS® Oil Database:

http://adios.orr.noaa.gov

## Where to find data

The collection of oil records that NOAA maintains is found on gitHub here:

https://github.com/NOAA-ORR-ERD/noaa-oil-data

That is a collection of JSON files, one for each record. This package is essentially a tool for manipulating that data.

Anyone, of course, could maintain their own collection of data.

## Documentation:

The documentation for this package is in this source repo
in `adios_db/Documentation/API_docs/` as a Sphinx doc, and published at:

https://noaa-orr-erd.github.io/adios_oil_database/



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





