#!/usr/bin/env python
"""
The correct conversion from C to K is 273.16

But a lot of data sources (notably the ADIOS2 database)
use 273.0.

So we end up with temps like: -0.15 C instead of 0.0 C
This script will "correct" that.
"""
from adios_db.scripts import run_json_through_oil_object
from adios_db.models.common.measurement import Temperature

# set the Tempurature object to apply the fix
Temperature.fixCK = True

# then run it all through
run_json_through_oil_object.run_through()
