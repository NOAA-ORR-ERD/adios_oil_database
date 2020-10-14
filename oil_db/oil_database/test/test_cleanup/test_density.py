"""
tests for density related cleanup
"""

import pytest

from oil_database.models.oil.oil import Oil
from oil_database.models.oil.measurement import (DensityPoint,
                                                 DensityList,
                                                 Density,
                                                 Temperature,
                                                 )

from oil_database.models.oil.sample import (Sample)
from oil_database.models.oil.sample import (PhysicalProperties)


from oil_database.models.cleanup.density import FixAPI


def no_api_with_density():

    oil = Oil(oil_id='XXXXXX')

    print(oil)
    print(oil.sub_samples)
    s = Sample()
    oil.sub_samples.append(s)
    # add some densities
    p = PhysicalProperties()
    s.physical_properties = p
    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="kg/m^3"),
                     ref_temp=Temperature(value=15.0, unit="C")),
        DensityPoint(density=Density(value=0.99, unit="kg/m^3"),
                     ref_temp=Temperature(value=25.0, unit="C"))
    ])

    return oil


def test_add_density():
    oil = no_api_with_density()

    # before adding:
    assert oil.metadata.API is None

    fixer = FixAPI(oil)
    results = fixer.check()

    print(results)

    assert False
