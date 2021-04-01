.. _managing_the_data:

#################
Managing the Data
#################

In order to manage the data, you'll want to work with the :py:class:`Oil` object.

The Oil object is essentially a Python class that mimics the base JSON format. It then provides attributes that let you "drill down" to find the data you want.


The Scripting Module
--------------------

Most of the things you'll need for "typical" work with the data can be found in the :py:mod`scripting` module. We recommend that you import itlke so:

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
arbitrarily nested lists, dicts, strings, numbers, and booleans.

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

You can create an empty Oil object from scratch -- this is likely to be useful for creating data from other data sources: CSV files, databases, etc. It does require a fairly in-depth knowledge of the nested structure, however.

.. code-block:: python

  oil = ads.Oil('XXXXX')

The only required argument is an oil_id: it can be any moderate-length string. Your ID scheme should match the database you are working with.

For other arguments, see: :py:class:`adios_db.scripting.Oil`


Example Scripts
---------------

There are a number of example scripts in the top-level scripts directory in the source code.

``adios_db/scripts``

These are various scripts used to do one-off cleanup or manipulation of the data. It is unlikely that you will want to run any of these directly, but they can be used as examples to follow.



