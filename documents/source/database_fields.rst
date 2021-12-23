######################
Fields in the database
######################

The following are general descriptions of the data stored in the database.

For a more technical detail of data in the database, see the ADIOS Data Model documentation
(currently unpublished -- reach out to us at: ``adios@orr.noaa.gov`` for information).

Record Metadata
===============

Various fields that describe the record itself, rather than particular measured data


Name
----
A human-readable name for the record -- ideally unique. There is no standard for naming petroleum products, but a name that generally describes the product, where it came from, etc, is good.


Additional Identifiers
----------------------

A list of other names, etc. that may be applied to this record, e.g. the region, field name, etc. Important is that these names are specific to the particular record -- not generic descriptions. “Macondo” and “MC 252” might be used for oil from the Deepwater Horizon incident. But “diesel” or "crude" is not specific to any one record -- “diesel” would be appropriate for a label, however.

Source Identifier
-----------------

Identifier used by the source of the data: the lab that did the analysis, etc. This is intended to be a short ID, not a description. The human-readable names should be in the name or additional identifier. But this is useful if you need to go back to the original source for more info.

Reference
---------

The full bibliographic reference, it has two components:

Year: year of publication

Reference: The complete bibliographic reference, ideally in a standard form (APA, Chicago, etc).

Example: “Hollebone B. "Physical Properties and Behaviour Measurements of Alaskan North Slope [2013] Crude Oil", Environment Canada, Ottawa, Ontario, Canada, May 2013”


Sample Date
-----------

The date the sample was taken from the source, or received by the lab.

Location
--------

Location of source of oil (well, etc)

Example: "Alberta, Canada"

Location Coordinates
--------------------

Georeferenced location of source of oil (well, etc). This can be a single point or a simple polygon delineating a region, in latitude-longitude coordinates (WGS84)

Product Type
------------

The Product Type is a broad identifier of the general class of product. It can be interpreted by users to, at a quick glance, know what the product is. It can also potentially be used by models to select appropriate algorithms to apply to the product. Essentially, the product type defines what the product “is”.

The Product Type must be one of a set list, outlined below. Every record belongs to one and only one product type. If a record is for a product that does not fit into any product type, it can be typed as “other”. Note: “NOS” means “Not Otherwise Specified”. The current list of product types used by the ADIOS Oil Database is:

|
| Crude Oil NOS
| Tight Oil
| Condensate
| Bitumen Blend
| Bitumen
| Refined Product NOS
| Fuel Oil NOS
| Distillate Fuel Oil
| Residual Fuel Oil
| Refinery Intermediate
| Solvent
| Bio-fuel Oil
| Bio-Petro Fuel Oil
| Natural Plant Oil
| Lube Oil
| Dielectric Oil
| Hydraulic Fluid
| Other
|

Labels
------
Assorted “tags” applied to the data  The primary goal is to have these be searchable. If someone ls looking for “fuel oil #2”, they should find all the number 2 fuel oils.

While a given record is one and only one Product Type, which defines what the product is, a record can have any number of labels, which are more or less what a product might be “called”, One of the reasons labels are useful is that petroleum products have many overlapping naming and categorizing systems. e.g. a Diesel Fuel is a Distillate Fuel Oil, it can be called “diesel” or “number 2 fuel oil”. These are intended to be more generic than additional identifiers -- it is expected that a lot of records will have any given label.

Comments
--------

The comments section includes an additional information about the record that is not captured in the fixed fields.

API Gravity
-----------

The API Gravity of the product. API is used primarily for reference, searching, etc. It should match the density at 60F. API is a particular unit for density at 60F (approximately 15C). It should only used for reference -- the included density data should be used for modeling, etc.

Score
-----

The completeness score (“Score”) in the data table is a rough assessment of how complete the data record is, from the perspective of oil fate modeling. A higher score should result in more accurate model results. The score is computed as follows:

The scores are normalized by the total possible score, resulting in a score between 0 and 100

Fresh oil:
..........

* One density. Score = 1

* Second density separated by temperature. Score = deltaT/40 but not greater than 0.5

* One viscosity. Score = 0.5

* Second viscosity at a different temperature. Score = maxDeltaT/40, but not greater than 0.5 

* Two Distillation cuts separated by mass or volume fraction.  Score = 3*maxDeltaFraction

* Fraction recovered <1. Score = 1.

One Weathered Subsample:
------------------------

* Density. Score = 1

* Viscosity. Score = 1

* One emulsion water content in any subsample. Score = 2.5

GNOME Suitable
--------------

The GNOME Suitable flag is an indicator of whether the record can be used in the NOAA GNOME oil weathering model. It means that the record meets the minimum requirements to be used in GNOME Oil -- that is, it won't crash the model. It is not an indicator that it is a very complete record. The Completeness Score should be used to evaluate how accurate model results might be.


Sub-samples
===========

Often when oil an analyzed in a lab, the original sample will be processed in some way, and the processed sample will be analysis separately. POssilbe processing includes artificial weathering in a lab and distillation.

Each record will have at least one sub sample, usually called "fresh oil"

If a record contains data about addisiton subsamples the sub-samples can have specific (optional) data that describes it.

Name
----
The name given to this sample

Example: Fraction left after Rotovap to 25% mass loss

Short Name
----------

An abbreviated form of the name that can be displayed easily

Example: 25% evaporated

Description
-----------
Any text that describes the sub sample

Example:  “Sample weathered to 24% mass loss with a rotovap, follwing teh standard protocol of the ESTS lab”

Sample ID
---------

An ID for the sub sample: each lab might have its own system for identifying their subsamples

Evaporated Fraction
-------------------

Some oil samples are evaporated artificially and this is the mass from loss in that process, if applicable

Boiling Point Range
-------------------
Some oil samples are fractions collected through fractional distillation and are characterized by a boiling point range.


Physical Properties
===================

Distillation Data
=================

SARA
=====

Environmental Behavior
======================

Compounds
=========

Bulk Composition
================

Industry Properties
===================



