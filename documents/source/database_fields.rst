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
A human-readable name for the record -- ideally unique. There is no standard for naming petroleum products, so the name in the database is the name provided by the source of the data.
It often, but not always, contains the type of oil and/or location of the source.


Additional Identifiers
----------------------

A list of other names, etc. that may be applied to this record, e.g. the region, field name, etc. Important is that these names are specific to the particular record -- not generic descriptions. “Macondo” and “MC 252” might be used for oil from the Deepwater Horizon incident. But “diesel” or "crude" is not specific to any one record -- “diesel” may be used as a label, however.

Source Identifier
-----------------

Identifier used by the source of the data: the lab that did the analysis, etc. This a short ID, not a description. This can be is useful if you need to go back to the original source (see the reference) for more info.

Reference
---------

A bibliographic reference for the source.

Example: “Hollebone B. "Physical Properties and Behaviour Measurements of Alaskan North Slope [2013] Crude Oil", Environment Canada, Ottawa, Ontario, Canada, May 2013”

Year: year of publication

Reference Year
--------------

The year of the reference

Sample Received Date
--------------------

Date sample was received in the laboratory doing the analysis, if available.


Location
--------

Location of source of oil (well, etc) Example: "Alberta, Canada"

For crude oils, this is usually the location of the well. For refined products, it may the the location of the refinery, or the point of sale.


Product Type
------------

The Product Type is a broad identifier of the general class of product. It can what the product is. Essentially, the product type defines what the product “is”.

The Product Type is one of a set list, outlined below. Every record belongs to one and only one product type. If a record is for a product that does not fit into any product type, it is typed as “other”. Note: “NOS” means “Not Otherwise Specified”. The current list of product types used by the ADIOS Oil Database is:

Crude Oil NOS:
    A "standard" crude oil that does not fit into any of the more specific types of crude oils.

Tight Oil:
    A type of oil found in impermeable shale and limestone rock deposits. Also known as “shale oil”, tight oil is extracted using hydraulic fracturing, or “fracking”.

Condensate:
    A low-density mixture of hydrocarbon liquids that have condensed to a liquid state during natural gas production.

Bitumen Blend:
    Bitumen (or other very heavy crude) blended with a lighter oil in order to be easier to ship and process. Often known as "Dilbit" or "Synbit"

Bitumen:
    A black, oily, highly viscous form of petroleum, a naturally-occurring organic byproduct of decomposed plants.

Refined Product NOS:
    A product of a refining process that is not one of the more specific refined product types.

Fuel Oil NOS:
    A fuel oil that is not one of the more specific fuel oils types.

Distillate Fuel Oil:
     A general classification for one of the petroleum fractions produced in conventional distillation operations.

Residual Fuel Oil:
     A general classification for the heavier oils, known as No. 5 and No. 6 fuel oils, that remain after the distillate fuel oils and lighter hydrocarbons are distilled away in refinery operations.

Refinery Intermediate:
    A product produced in a refinery that is not a final end use product, but rather used as part of further refining and product production.

Solvent:
    A petroleum product used as an industrial solvent

Bio-fuel Oil:
    Fuel oil made from biological sources, such as biodiesel.

Bio-Petro Fuel Oil:
    A blend of Bio fuel oil and a petroleum based fuel oil.

Natural Plant Oil:
    Plant oil that has not been processed into a fuel.

Lube Oil:
    Oil produced to be used a lubricant

Dielectric Oil:
    Oil used for its electrical properties. Sometimes called "transformer oil". These can be petroleum based to synthetic.

Hydraulic Fluid:
    Fluid used to transfer power in hydraulic machinery. Common hydraulic fluids are based on mineral oil or water, nd can have a wide varierty of properties.

Other:
    A product that does not fit into any of the other Product Type categories.


Labels
------
Assorted “tags” or "keywords", or "names" that could be used to name a record. These can be helpful when searchign for a particular product.

While a given record is one and only one Product Type, which defines what the product is, a record can have any number of labels, which are more or less what a product might be “called”.

One of the reasons labels are useful is that petroleum products have many overlapping naming and categorizing systems.
e.g. a Diesel Fuel is a Distillate Fuel Oil, it can be called “diesel” or “number 2 fuel oil”.
These are intended to be more generic than additional identifiers -- it is expected that a lot of records will have any given label.


Comments
--------

Any additional information about the record that is not captured in the fixed fields.

API Gravity
-----------

The API Gravity of the product. API is a particular unit for density at 60F (approximately 15C). It should only used for reference -- the included density data should be used for modeling, etc.

Score
-----

The completeness score (“Score”) is a rough assessment of how complete the data record is, from the perspective of oil fate modeling. A higher score should result in more accurate model results. The score is computed as follows:

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

GNOME Compatible
----------------

The GNOME Compatible flag is an indicator of whether the record can be used in the NOAA GNOME oil weathering model. It means that the record meets the minimum requirements to be used as a GNOME Oil -- that is, it won't crash the model. It is not an indicator that it is a very complete record. The Completeness Score should be used to evaluate how accurate model results might be.


Sub-samples
===========

Often when oil an is analyzed in a lab, the original sample will be processed in some way, and the processed sample will be analysis separately. Possible processing includes artificial weathering in a lab and distillation.

Each record will have at least one sub-sample, usually called "fresh oil"

If a record contains data about additional sub-samples the sub-samples may have specific (optional) data that describes it.

Name
----

The name given to this sub-sample


Description
-----------

Text that describes the sub sample.

Sample ID
---------

An ID for the sub sample: each lab might have its own system for identifying their sub-samples.


Evaporated Fraction
-------------------

Some oil samples are evaporated artificially and this is the mass from loss in that process, if applicable.


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



