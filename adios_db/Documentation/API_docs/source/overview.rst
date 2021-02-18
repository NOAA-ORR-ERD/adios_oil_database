########
Overview
########

``adios_db`` is a package that provides facilities for working with petroleum products data for oil spill response. It is used to support the NOAA ADIOS Oil Database project:

adios-stage.orr.noaa.gov

The data conforms to the NOAA ADIOS Data Model.

Fundamentally, the package provides a set of Python objects that represent the data model. Each of these object can save itself to / load itself from JSON data.

At the top level is the :py:class:`Oil` object, which represents a single oil Record.

At the bottom level is the :py:class:`Measurement` representing a single measurement. There are a set of ``Measurement`` subclasses representing different physical unit types, so that the units can be properly maintained, converted, etc.



