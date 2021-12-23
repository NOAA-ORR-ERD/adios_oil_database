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
    result in more accurate forecasts in the model.
  - **Suitable for GNOME** This flag indicates whether an oil record can be used with the GNOME oil weathering model. Note: This only indicates that is *can* be used. Whether it's a good record should be determined by looking at the Score.


The list is sorted alphabetically by name but if you click on the column headers you can see it sorted by that field.


The Search Box
..............

If you type any text in the search box, the list will be reduced to those records that have the text in any part of the Name, Location, or Product Type. So typing in "IFO" will result in finding oils from Cal**IFO**rnia, as well as any oil with "IFO" in the name, and all oils in the "Intermediate Fuel Oil" Category.

Product Type
............

The oils in the database are all sorted into various types of oils: crude or refined products, etc. If a type is selected, only oils that fit that type will be displayed. Some of the types are broad and overlapping, for instance, in "Distillate Fuel Oil", you will find both Gasoline and Kerosene.

If you are looking for a product that fits within a certain type of oil, selecting that type will help you refine your search quickly.


API slider
..........

The API slider lets you set a range you want of the oil's API gravity. Only oils that fall within that range will be displayed.


Viewing the Complete Oil Record
-------------------------------

Clicking on the oil name in the list brings you to the oil's Physical properties tab for a Fresh Oil Sample.

