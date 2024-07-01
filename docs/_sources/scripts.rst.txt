.. _scripts:

#################################
Scripts for working with the data
#################################

A number of top-level scripts are installed along with the python package. If the package is installed inot a Python installation that is set up correctly, you shoujld be able to invoke the scripts directly, e.g. ::

  adios_db_validate dir_to_validate

The scripts all begin with `adios_db_` -- if you have command-line completion, you should be able to see them all with a <tab><tab>

The Installed scripts
=====================

Scripts for working with the JSON files
---------------------------------------

adios_db_validate
.................

This generates validation reports from all the JSON files in the provided directory.
You must provide a directory to validate, and it will search in that dir, and any child dirs for .JSON files to validate.

Example::

    adios_db_validate oil/EC


adios_db_process_json
.....................

This processes a set of JSON files in the provided directory.
It will load them into a adios_db `Oil` object and save it out again as JSON.
This serves to make sure the JSON is valid, and normalizes the JSON with the same white space and data order, so that files with non-meaningful changes will compare equal.

You must provide a directory to process, and it will search in that dir, and any child dirs for .JSON files to process.

Example::

    adios_db_process_json noaa_oil_data/data/oil

will process all the records in the noaa_oil_data repository.

NOTE: this should always be run before merging any new or edited data into the repository.

Optionally, "dry_run" can be passed on the command line to make sure the JSON is all valid, but without making any changes to the data.

adios_db_read_noaa_csv
......................

Reads a "NOAA standard CSV file" and generates an adios_db JSON file from the data. ::

    adios_db_read_noaa_csv name_of_the_file.csv

NOAA standard CSV files are ones that conform to the NOAA Excel template format:

:download:`ADIOS data template <../../../data/ADIOS_data_template.xlsx>`

If the file will not load, and the error is not obvious, you can pass the ``--debug`` flag, and you will get a **lot** or additional information about what the script is trying to do.


adios_db_assign_ids
...................

Assign IDs to a set of new records. ::

    adios_db_assign_ids PREFIX [dry_run] data_dir, file1, file2, file3, ...

``PREFIX`` is the 2-letter prefix you want to useL, e.g. AD. It can be a new prefix, or an existing one.

``data_dir`` is a directory with the existing data -- it will be scanned to determine which IDs are already in use, so new non-conflicting ones will be generated.

You can pass in one or more JSON files, e.g. ``*.json``

If ``dry_run`` is on the command line, it will report what it would do,
but not save any changes


adios_db_add_labels
...................

This script will add likely labels to the records, based on a set of criteria developed int eh code -- it will not correctly label everyting, but should give you a good start.

::

  adios_db_add_labels data_dir [dry_run]

``data_dir`` is the dir where the data are: the script will recursively search for JSON files

If ``replace`` is on the command line, existing labels with be replaced.
Other wise, new ones will be added, but none removed.

If ``dry_run`` is on the command line, it will report what it would do, but not save any changes


Scripts for working with the web application / Mongo DB:
--------------------------------------------------------

adios_db_init
.............

adios_db_import
...............

adios_db_oil_query
..................

adios_db_backup
...............

adios_db_restore
................

Scripts for working with the code / tests
-----------------------------------------

adios_db_update_test_data
.........................

This will update the test data with the latest version from NOAA oil data. This should only be run by people working on the ``adios_db`` codebase.



