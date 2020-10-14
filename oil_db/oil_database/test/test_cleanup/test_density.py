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

    # create a sample for fresh oil
    s = Sample()

    # add some densities
    # p = PhysicalProperties()
    p = s.physical_properties
    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="kg/m^3"),
                     ref_temp=Temperature(value=15.0, unit="C")),
        DensityPoint(density=Density(value=0.99, unit="kg/m^3"),
                     ref_temp=Temperature(value=25.0, unit="C"))
    ])

    oil.sub_samples.append(s)

    return oil

def test_check_no_API():
    oil = no_api_with_density()

    fixer = FixAPI(oil)
    results = fixer.check()

    assert results.startswith(f"Cleanup: {fixer.ID}:")
    assert "No API value provided" in results


def test_check_API_is_there():
    oil = no_api_with_density()
    oil.metadata.API = 32.0

    fixer = FixAPI(oil)

    results = fixer.check()

    assert results is None


def test_add_density():
    oil = no_api_with_density()

    # before adding:
    assert oil.metadata.API is None

    fixer = FixAPI(oil)

    print(results)

    assert results
    assert False
