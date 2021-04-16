A place to put data for testing.

note: not called "test_data", so pytest won't think it has tests in it

The noaa-oil-data dir should have JSON records that are a subset of the official noaa data -- it should be updated to be in sync with those records as they are updated. The::

scripts/update_test_data_from_noaa_repo.py

script should be run when things change in the database.

Records in the example_data are JSON records that are used for specific tests -- they may not be "real data", but rather designed for some specific purpose. These should be "run through" the Oil object to keep the format up to date and consistent.






