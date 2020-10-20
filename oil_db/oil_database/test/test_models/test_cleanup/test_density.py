"""
tests for density related cleanup
"""

from math import isclose
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
        DensityPoint(density=Density(value=0.8751, unit="g/cm^3"),
                     ref_temp=Temperature(value=15.0, unit="C")),
        DensityPoint(density=Density(value=0.99, unit="g/cm^3"),
                     ref_temp=Temperature(value=25.0, unit="C"))
    ])

    oil.sub_samples.append(s)

    return oil


def test_check_no_API():
    oil = no_api_with_density()

    fixer = FixAPI(oil)
    print("in test: API:",oil.metadata.API)

    results = fixer.check()

    assert results.startswith(f"Cleanup: {fixer.ID}:")
    assert "No API value provided" in results


def test_check_API_is_there():
    """
    if there is an API, check() should return tehempty string
    """

    oil = no_api_with_density()
    oil.metadata.API = 32.0

    fixer = FixAPI(oil)

    results = fixer.check()

    assert results is ""


def test_add_density():
    oil = no_api_with_density()

    # before adding:
    assert oil.metadata.API is None

    fixer = FixAPI(oil)

    fixer.cleanup()

    assert isclose(oil.metadata.API, 30.06, rel_tol=1e4)


def test_find_density_near_15C():
    oil = no_api_with_density()

    fixer = FixAPI(oil)

    result = fixer.find_density_near_15C()

    assert result == 875.1


def test_find_density_near_15C_none():
    oil = no_api_with_density()

    oil.sub_samples[0].physical_properties.densities[0].ref_temp.value = 17.0
    fixer = FixAPI(oil)

    result = fixer.find_density_near_15C()

    assert result is None




