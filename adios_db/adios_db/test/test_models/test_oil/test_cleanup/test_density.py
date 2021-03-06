"""
tests for density related cleanup
"""

from math import isclose

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.physical_properties import (DensityPoint,
                                                     DensityList,
                                                     )
from adios_db.models.common.measurement import (Density,
                                                Temperature,
                                                )

from adios_db.models.oil.sample import (Sample)

from adios_db.models.oil.cleanup.density import FixAPI


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
    print("in test: API:", oil.metadata.API)

    flag, msg = fixer.check()

    assert flag is True

    assert msg.startswith(f"Cleanup: {fixer.ID}:")
    assert "No API value provided" in msg


def test_check_API_is_there():
    """
    if there is an API, check() should return the empty string
    """

    oil = no_api_with_density()
    oil.metadata.API = 32.0

    fixer = FixAPI(oil)

    flag, msg = fixer.check()

    assert flag is None
    assert msg == 'API is fine'


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

def test_find_density_near_15C_two_values():
    """
    these are data that failed with earlier version

    [(995.0, -0.14999999999997726),
     (989.0, 14.850000000000023)]
    """

    oil = no_api_with_density()
    densities = oil.sub_samples[0].physical_properties.densities

    densities[0].density.value = .995
    # densities[0].density.unit = 'kg/m^3'
    densities[0].ref_temp.value = -0.14999999999997726

    densities[1].density.value = .989
    # densities[0].density.unit = 'kg/m^3'
    densities[1].ref_temp.value = 14.85


    fixer = FixAPI(oil)

    result = fixer.find_density_near_15C()

    assert isclose(result, 989.0, rel_tol=1e3)


def test_find_density_near_15C_none():
    """
    if there are no density values, then this should not add an API
    """
    oil = no_api_with_density()

    oil.sub_samples[0].physical_properties.densities = DensityList()
    fixer = FixAPI(oil)

    result = fixer.find_density_near_15C()

    assert result is None




