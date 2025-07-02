
.. _computation:

###############################
Computation with the ADIOS data
###############################

The core ``Oil`` object system was designed for managing the data -- lots of detail about exactly what data is there, the ability for anything to be missing, and units clearly defined with each value.

However, this makes it a bit awkward to work with if you want to do computation.

The :py:mod:`computation` sub-package provides a number of utilities that make it easier to do computation with the data.


The Measurement Objects
=======================

At the base of the entire set of data structures are :py:class:`Measurement` objects. A ``Measurement`` object is used to store the actual data, along with its units, and a few utilities for unit conversion etc.

Features of a ``Measurement`` Object.

* Unique object type for each physical unit type, e.g. Mass, Length, etc.
* Stores the unit of the data
* Can store single value, as well as a range of values, or greater than or less than a given value.
* Supplies unit conversion to other compatible units.

.. note:: The ``Measurement`` objects use the ``pynucos`` package for all unit defintions and conversions. See: `PyNUCOS on GitHub <https://github.com/NOAA-ORR-ERD/PyNUCOS>`_ for unit types, names, etc.

Available Measurement classes:

``AngularVelocity``,
``AnyUnit``,
``Concentration``,
``Density``,
``Dimensionless``,
``DynamicViscosity``,
``InterfacialTension``,
``KinematicViscosity``,
``Length``,
``Mass``,
``MassFraction``,
``MassOrVolumeFraction``,
``MeasurementBase``,
``MeasurementDataclass``,
``NeedleAdhesion``,
``Pressure``,
``SayboltViscosity``,
``Temperature``,
``Time``,
``Unitless``,
``VolumeFraction``

Examples
--------

Single Value:
.............

.. code-block:: ipython

    # All the ``Measurement`` objects should be in the scripting namespace
    import adios_db.scripting as ads

    In [4]: mass_recovered = ads.Mass(54, 'kg')

    In [5]: mass_recovered
    Out[5]: Mass(value=54.0, unit='kg', unit_type='mass')

    # create a new Object with different units
    In [6]: mass_recovered.converted_to('g')
    Out[6]: Mass(value=54000.0, unit='g', unit_type='mass')

    # change units in place:
    In [7]: mass_recovered.convert_to('g')

    In [8]: mass_recovered
    Out[8]: Mass(value=54000.0, unit='g', unit_type='mass')

    # get the value
    In [9]: mass_recovered.value
    Out[9]: 54000.0

    # and the unit
    In [10]: mass_recovered.unit
    Out[10]: 'g'

    # it will not let you convert to an invalid unit:

    In [11]: mass_recovered.convert_to('meter')

    ...

    InvalidUnitError: The unit: meter is not in the list for Unit Type: Mass


Range of Values:
................

You can specify a range of values for a measurement:

.. code-block:: ipython

    In [16]: pour_point
    Out[16]: Temperature(unit='C', min_value=15.0, max_value=20.0, unit_type='temperature')

    # The value is None:
    In [17]: pour_point.value

    The min and max are directly available:

    In [20]: pour_point.min_value
    Out[20]: 15.0

    In [21]: pour_point.max_value
    Out[21]: 20.0

    # or you can find the minimum or maximum
    # if there is a single value, it will be returned
    In [18]: pour_point.minimum
    Out[18]: 15.0

    In [19]: pour_point.maximum
    Out[19]: 20.0

Greater than or less than values:
.................................

You can specify only a minimum or maximum, to represent greater-than or less-than, for example a measurement below a detection limit might be less than a given value:

.. code-block:: ipython

    In [22]: benzene_concentation = ads.MassFraction(max_value=1, unit='ppb')

    In [23]: benzene_concentation
    Out[23]: MassFraction(unit='ppb', max_value=1.0, unit_type='massfraction')

    In [24]: benzene_concentation.maximum
    Out[24]: 1.0

    In [25]: benzene_concentation.converted_to('ppm').maximum
    Out[25]: 0.001

Similarly for greater than.
