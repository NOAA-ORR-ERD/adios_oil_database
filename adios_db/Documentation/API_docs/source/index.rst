.. ADIOS Oil Database documentation master file, created by
   sphinx-quickstart on Thu Jan 28 16:08:19 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ADIOS Oil Database's documentation!
==============================================

There are two things one might want to do with this package:

1) Manage the data itself: search it, update it, add to it etc.
   See: :ref:`managing_the_data` for some documentation of this use case.

2) Extract numerical values from the data to use for computation,
   such as initializing an oil weathering model.
   See: :ref:`computation` for some documentation of this use case.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   managing
   computation
   importing_new_data

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/adios_db.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
