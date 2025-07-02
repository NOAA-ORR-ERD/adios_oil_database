ADIOS Oil Database ``adios_db`` package
=======================================

The ``adios_db`` package is a Python package developed to help manage and work with oil properties data, as managed in the ADIOS\ :sup:`®` Oil Database project:

http://adios.orr.noaa.gov

This package is used to provide the back-end services of the ADIOS\ :sup:`®` Oil Database web application, and can also be used to work with the data directly itself.


There are three things one might want to do with this package:

1) Manage the data itself: search it, update it, add to it etc.
   See: :ref:`managing_the_data` for some documentation of this use case.

2) Extract numerical values from the data to use for computation,
   such as initializing an oil weathering model.
   See: :ref:`computation` for some documentation of this use case.

3) Extracting data needed for modeling. Oil weathering models need oil properties in order to apply the model to a particular oil. But each model requires different data, and each oil record provides different data. So building a "model oil" is non-trivial. See :py:mod:`adios_db.computation.gnome_oil` for an example of how an `Oil` object as required by the GNOME oil weathering model is constructed from the data. Other models should be able to be supported with similar code.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   scripts
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
