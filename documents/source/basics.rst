##########################
Selecting and Viewing Oils 
##########################

Selecting an Oil
----------------

The database comes with a Selection interface that allows you to search for oils in a number of ways, and see all the data associated with a particular oil. 

The list view presents the records that meet the current selection criteria -- this is the full set initially. This list includes only a subset of the fields in the individual oil records. These include:

  - **Name:** The name of the oil.
  - **Location:** The region the oil came from.
  - **API:** The oil's API Gravity (density).
  - **Score:** An estimate of the completeness of the record.
    Records with higher quality scores have more data and will
    result in more accurate forecasts in models The range is from 0-100.
  - **Compatible with GNOME** This flag indicates whether an oil record can be used with the GNOME oil weathering model.
    Note: This only indicates that is *can* be used. Whether it's a good record for the use case should be determined by looking at the Score or the record itself.


The list is sorted alphabetically by name but if you click on the column headers you can see it sorted by that field in the column clicked on.


The Search Box
..............

If you type any text in the search box, the list will be reduced to those records that have the text in any part of the ID, Name, Location, or Product Type. So typing in "IFO" will result in finding oils from Cal**IFO**rnia, as well as any oil with "IFO" in the name. If you are searching for a particular type a product, it may be better to specify the *Product Type* or *labels*.

If you happen to know the ADIOS ID -- you can type that in the search bos to get directly to that oil.

Product Type
............

The oils in the database are all sorted into various types of product: crude or refined products, etc. If a type is selected, only oils of that type will be displayed. Some of the types are broad and overlapping, for instance, in "Distillate Fuel Oil", you will find both Gasoline and Kerosene.

If you are looking for a product that fits within a certain type of oil, selecting that type will help you refine your search quickly.


API slider
..........

The API slider lets you set a range you want of the oil's API gravity. Only oils that fall within that range will be displayed.


Viewing the Complete Oil Record
-------------------------------

Clicking on the oil name in the list brings you to a page with all the data in that record.

At the top of the page is the record's metadata: name, reference, API, labels, etc.

Below that are tabs for each "subsample" of the oil. All records have a tab for the "Fresh Oil" -- some detailed records have additional subsamples with properties of the oil after having been processes in some way: artifiical weathing in a lab, for instance.

On each subsample tab, there are tabs for:

* Physical Properties
* Distillation Data
* Compounds
* Bulk Composition
* Environmental Behavior
* Industry Properties
* Metadata

Click in the appropiate tab to see the associated data.

Downloading the Data
--------------------

When viewing and oil record, you can click the "Download" button to download a JSON file with all the oil data.

This file can be directly used by the GNOME system (PyGNOME and WebGNOME), as well as processed by other computerized systems.

See the `ADIOS Oil Database Project <https://github.com/NOAA-ORR-ERD/adios_oil_database>`_ on gitHub for more detail, and a Python library for working with the data.

JSON is a text file format for structured data, widely used for data interchange: https://www.json.org/json-en.html
