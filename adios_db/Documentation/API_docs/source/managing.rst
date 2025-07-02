.. _managing_the_data:

#################
Managing the Data
#################

In order to manage the data, you'll want to work with the ``Oil`` object.

The Oil object is essentially a Python class that mimics the base JSON format. It then provides attributes that let you "drill down" to find the data you want.


The Scripting Module
--------------------

Most of the things you'll need for "typical" work with the data can be found in the
``adios-db.scripting`` module. We recommend that you import it like so:

.. code-block:: python

  import adios_db.scripting as ads

Then you can access all the needed functions an objects from the ``ads`` name.

Working with JSON
-----------------

For the most part, the data are stored as JSON: either in MongoDB, or as JSON files on disk.

JSON-compatible-Python
......................

A subset of JSON can be mapped directly to Python builtin objects.
We call this "JSON-compatible-Python", or ``py_json`` for short.
Essentially, it is Python that can be saved-to and loaded-from JSON losslessly:
arbitrarily nested lists, dicts, strings, numbers, and bools.

Creating an ``Oil`` object
..........................

The ``Oil`` object (and all the sub-objects) can be created from py_json with:

.. code-block:: python

  oil = ads.Oil.from_py_json(a_json_compatible_object)

or directly from a json file with:

.. code-block:: python

  ads.Oil.from_file(a_file_path)

The file path can be a string or ``pathlib.Path`` object (you can also pass in an open file object).


Saving an ``Oil`` object
........................

An ``Oil`` object (and all the sub-objects) can be saved to py_json with:

.. code-block:: python

  python_object = oil.py_json()

or directly to a json file with:

.. code-block:: python

  an_oil.to_file(a_file_path)

The file path can be a string or ``pathlib.Path`` object

(you can also pass in an open file object)


Creating an Oil from scratch
----------------------------

You can create an empty ``Oil`` object from scratch -- this is likely to be useful for creating data from other data sources: CSV files, databases, etc. It does require a fairly in-depth knowledge of the nested structure, however.

.. code-block:: python

  oil = ads.Oil('XXXXX')

The only required argument is an oil_id: it can be any moderate-length string. Your ID scheme should match the database you are working with.

For other arguments, see: :py:class:`adios_db.scripting.Oil`

.. note:: Hopefully we will someday write complete documentation for how to create a full oil record from scratch. Below are a few pieces. In the meantime, you can look at the tests and at the included import scripts to see how the pieces are created and put together.

The ``Oil`` attributes
......................

See :py:class:`adios_db.models.oil.oil.Oil` for the full details. but in short, a basic ``Oil`` object has:

- ``oil_id``: the ID for the record

- ``metadata``: where the metadata goes -- name, product types, etc: :py:class:`adios_db.models.oil.metadata.Metadata`

- ``subsamples``: A list of data about the samples.
  This is where the actual data goes. Every record should have at least one subsample -- the zeroth one should be the "fresh oil" as it arrived at a lab.
  Other subsamples will have been processes on some way.

``Sample``
..........

The :py:class:`adios_db.models.oil.sample.Sample` class holds all the measurements recorded in the record.

It is broken down into different categories of data -- see the API docs for details

``Distillation``
................

The :py:class:`adios_db.models.oil.distillation.Distillation` holds distillation cut data.
It contains information about the distillation process, and the cut data itself.
The distillation cuts are stored in a distillation cut list, with a set of fraction: temperature pairs. The is a utility constructor to generate the cut list from arrays of data. For example:

.. code-block:: python

    from adios_db.models.oil.distillation import Distillation, DistCutList
    from adios_db.models.common.measurement import Temperature, Concentration

    fractions = (1.5, 2.8, 12.4, 23.5, 44.3, 63.9, 82.7, 91.7, 96.2, 98.8)
    temps = (36.0, 69.0, 119.0, 173.0, 283.0, 391.0, 513.0, 604.0, 672.0, 729.0)

    dct = DistCutList.from_data_arrays(fractions=fractions,
                                       temps=temps,
                                       frac_unit='percent',
                                       temp_unit='C'
                                       )

    # and now a Distillation object can be created

    dist_data = Distillation(type="mass fraction",
                             method="some arbitrary method",
                             end_point=Temperature(value=15, unit="C"),
                             fraction_recovered=Concentration(value=0.8,
                                                              unit="fraction"),
                             cuts=dct
                            )

    # this can be added to the Sample:
    sample.distillation_data = dist_data

    # which could be in an Oil object:
    sample = oil.sub_samples[0].distillation_data = dist_data


Example Scripts
---------------

There are a number of example scripts in the top-level scripts directory in the source code.

``adios_db/scripts``

These are various scripts used to do one-off cleanup or manipulation of the data. It is unlikely that you will want to run any of these directly, but they can be used as examples to follow.



