.. _importing_new_data:

##################
Importing New Data
##################

The ADIOS\ :sup:`®` Oil Database uses JSON as its native storage / interchange format.

In order to get a new record into the database, it must be converted to JSON somehow. How best to do that depends on the how the data are currently stored, and what tools one is familiar with.

Using the Python Library
========================

If you are familiar with Python, then using the ``adios_db`` Python package may be the easiest way to go. The library provides a set of nested Python objects that conform to our data model, and that can save themselves out to our JSON interchange format. See :ref:`managing_the_data` for details.

This would commonly be a way to get your data into ADIOS\ :sup:`®` Oil Database if it's already in a custom database or CSV files, or..

You can see some examples of import scripts in the :py:mod:`data_sources` package.


Utility functions to make importing easier
------------------------------------------

The full object hierarchy is fairly deeply nested, in order to provide full flexibility and make sure units are consistent, etc. To make it easier to build the data structures needed, a number of the "collections" have alternate constructors to build them from typical data. For example, to create a collection of density measurements:


.. code-block:: python

    data = [(0.8663, "g/cm³", 15, "C"),
            (0.9012, "g/cm³", 0.0, "C"),
            ]
    sample.physical_properties.density = DensityList.from_data(data)

creates a Density List structure (when exported to JSON) that looks like::

    [{'density': {'value': 0.9012, 'unit': 'g/cm³', 'unit_type': 'density'},
                  'ref_temp': {'value': 0.0, 'unit': 'C', 'unit_type': 'temperature'}},
     {'density': {'value': 0.8663, 'unit': 'g/cm³', 'unit_type': 'density'},
                  'ref_temp': {'value': 15.0, 'unit': 'C', 'unit_type': 'temperature'}},
    ]

Other handy constructors are:

.. code-block::

    DensityList.from_data()

    KinematicViscosityList.from_data()

    DynamicViscosityList.from_data()

    DistCutList.from_data_arrays()



Generate JSON Directly
======================

You can generate the JSON from your data directly, with whatever tools you may have on hand. The JSON format is documented, but the easiest way it probably to download a similar record from the database at:

http://adios.orr.noaa.gov

and match that JSON. Note that the JSON is "sparse" -- there is no need to include any fields that are not relevant.


Edit JSON by Hand
=================

JSON is a human-readable format, and to some extent human-writable, but writing full JSON by hand can be pretty challenging. However, editing JSON by hand is quite manageable, so if you start with a similar record, from:

http://adios.orr.noaa.gov

or

https://github.com/NOAA-ORR-ERD/noaa-oil-data

You can then hand edit the file to replace the data with values you want. We recommend you take the time to update the meta-data in the file. And almost everything in the format is optional, so you can simply remove fields that are not relevant to your problem.


Use a Standard CSV Format
=========================

In addition to our standard JSON, the package has an importer for a "standard" CSV file. These do not include every feature of the data model, but are easy to work with for a typical lab analysis with Excel. We provide an Excel template that can be filled out.

The template can be downloaded here: :download:`ADIOS data template <../../../data/ADIOS_data_template.xlsx>`


Using the Excel template
------------------------

It may help to be familiar with the ADIOS data model, but the goal is to have the template be straightforward and easy to fill out.

Use one worksheet for each record. If/when you save it out as a CSV file, be sure to save it in UTF8 encoding: "CSV-UTF8".

Note that it's OK to simply leave fields blank if there is no data -- the ADIOS\ :sup:`®` Oil Database is very forgiving of sparse data.

Multiple values
...............

In general, you don't want to touch any of the field names or descriptions, only the data entry cells. However, there are a number of places where ADIOS\ :sup:`®` Oil Database will accept "one or more" data points for a given property (e.g. density at different temperatures), so you are free to insert new rows to accommodate all your data.

Do make sure to insert an empty row in between "tables" of the same data type.

Units
.....

The units used for data are critical to include, and usually are kept in a separate cell from the values. Units should conform to the units used in the ADIOS\ :sup:`®` Oil Database -- which are specified in the NOAA "NUCOS" unit conversion system. The unit list is published here: https://github.com/NOAA-ORR-ERD/PyNUCOS/blob/master/NUCOS_unit_list.rst

However, allowable units conform to standard industry practice, and should be in pick lists in the Excel template.

The fields
..........

ADIOS Data Model Version
    Do not change this field -- it specifies which version of the data model this template can be used with. Do make sure to get the latest version of the template when you start new work.

Sections
........

The template is broken down into sections that correspond to the structure of the ADIOS\ :sup:`®` Oil Database. The sections are indicated with bold text in the template.

Record metadata
...............

Each record needs some information about the record itself. In general, a single record represents a single sample.
That sample may been been split to have different labs perform various analyses, but all the data should have come from the same sample.
For example, if a sample is taken from the same well at two different times, those should be treated as separate records.

Name
  A name for the record: it's pretty free form, but good to use something somewhat unique.

Source ID
   If the lab providing the data has its ID for this record, it can be provided here. It can be any short text.

Alternate Names
   Alternate names are common names that might refer to this record. For example, the record name may be "Mississippi Canyon 423", and an alternate name might be "South Louisiana Crude". There can be any number of alternate names, but they should not be about the oil type -- e.g. not "crude" or anything like that. Alternate names are used to help people find what they need in the database.

Location
    The general location of the source of the sample, could be a country, state, county, etc.

Reference
   If the data are published somewhere, this is the bibliographic reference. The year is stored separately.

Sample Date
    Date the sample was obtained, in the ISO data format: YYYY-MM-DD, e.g. 2021-06-28 for June 6, 2021. It can be just a year as well.

Product Type
   Product Type -- one of the product types used in the ADIOS\ :sup:`®` Oil Database. It specifies "what" the product is. Any given product has one and only one product type. Use one of the ones in the pick list, or see below for labels.

API
    API Gravity -- this is in the meta data for searching, etc. Actual density should be provided in the physical properties data.

Labels
    Labels are various ways one might refer to this record -- used for searching. For example, an oil might be called "Diesel" or "Fuel Oil #2", etc.
    It is best to pick labels from the current list used in the ADIOS\ :sup:`®` Oil Database.
    Both the labels and the mapping of labels to product types can be found in this CSV file: :download:`Mapping Product Types to Labels <../../../adios_db/models/oil/product_types_and_labels.csv>`

Location Coordinates
    Geographic coordinates of the source, if relevant (Decimal degrees, WGS84). If the source is a well, the coordinates can be a simple longitude-latitude point:  ``[28.324, -76.521]``, or if the location is a region (such as an oil field) it can be a polygon: an ordered list of multiple points:

    ``[(88.671327, 29.111853),(88.512073, 29.155960),(88.434388, 29.033772),`` ``(88.554800, 28.891036),(88.706286, -28.982817)]``

Comments
    The record can contain any free form text as comments. This is where to put notes about anything unusual or notable about the record that is not otherwise captured in the data model.

Subsample Metadata
..................

Some labs will have an original sample, and then also process the oil in some way and collect measurements about the processed data. These data are all part of the same record, but may have a completely new set of measurements associated with them. The data model is designed to handle arbitrary "subsamples", created in different ways, but the two common ones currently in the data are distillation fractions (from physical distillation) and lab-weathered samples, such as evaporated in a rotovap or "topped" to some temperature.

All records will have at least one subsample -- assumed to be the original (usually fresh oil).

Each subsample has its own metadata describing it.

Name
    A name for the subsample: e.g. "fresh oil" or "20% evaporated"

Short name
    A short name -- this is for the user interface, it should not be more than 20 characters or so. It can be the same as the name.

Sample ID
    Lab-specific ID for the subsample, if applicable

Description
    Text description of the subsample

Fraction evaporated
    If an evaporated subsample, the fraction lost (mass or volume fraction)

Boiling Point Range
    If a distilled subsample, the range of boiling points included.


Physical Properties
...................

This section covers the physical properties of the subsample.

Pour Point
    The subsample pour point

Flash Point
    The subsample flash point

Density
    The density of the subsample. Density varies with temperature, so there can be any number of density-temperature pairs. Add extra rows as needed.

Viscosity
    The viscosity of the subsample. Viscosity varies with temperature, so there can be any number of viscosity-temperature pairs. Add extra rows as needed.

Distillation Data
.................

Distillation can be done in various ways. In the template there are fields to specify the overall process in addition to the fields for the actual distillation cuts.

Type
    The type of distillation: "mass fraction" or "volume fraction"

Method
    The method used -- Ideally an ASTM standard or the like

Final Boiling Point
    Highest boiling point of any compound

Fraction Recovered
    Some simulated distillation methods don't account for all the oil -- perhaps only up to a certain boiling point. Fraction recovered is the fraction that is included in the distillation cuts. If all the oil is accounted for, this is 100%.

Distillation cuts
   The fraction and boiling point for each cut.

    Note: The initial boiling point should be listed as a 0% cut.

    Add extra rows as needed.


Compounds
.........

Compounds can be concentration measurements for zero or more individual compounds. Add as many rows as required. Each object in the list has the same structure including the following elements:

Name
    Name of the compound

Fraction
    Numerical value of the concentration measurement

Fraction unit:
    A pick list where the unit can be specified. Options include percent, ppm, g/kg, and mg/g.

Unit type:
    A pick list where the unit type can be specified. Options include mass fraction (m/m) or volume fraction (v/v).

Method:
    Name of the method used

Groups:
    Optional labels used to group related measurements together on the ADIOS interface. Examples include “BTEX”, “n-alkanes”, “PAHs”.


Bulk Composition
................

Bulk Composition includes concentration measurements for zero or more elemental analyses or groupings of compounds, such as sulfur content, wax content, or TPH. More examples are in the Common Data section below. Each object in the list has the same structure as those in the Compounds section. Add as many rows as required. 





