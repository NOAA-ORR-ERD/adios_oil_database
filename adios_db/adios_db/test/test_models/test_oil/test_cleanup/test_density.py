"""
tests for density related cleanup
"""
from math import isclose

from adios_db.models.common.measurement import Density, Temperature
from adios_db.models.oil.oil import Oil
from adios_db.models.oil.physical_properties import DensityPoint, DensityList
from adios_db.models.oil.sample import Sample
from adios_db.models.oil.cleanup.density import FixAPI


def no_api_with_density():
    oil = Oil(oil_id='XXXXXX')

    oil.metadata.product_type = "Crude Oil NOS"
    print(oil)

    # create a sample for fresh oil
    s = Sample()

    # add some densities
    p = s.physical_properties
    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="g/cm^3"),
                     ref_temp=Temperature(value=60.0, unit="F")),
        DensityPoint(density=Density(value=0.99, unit="g/cm^3"),
                     ref_temp=Temperature(value=25.0, unit="C"))
    ])

    oil.sub_samples.append(s)

    return oil


def no_api_with_one_density_13C():
    oil = Oil(oil_id='XXXXXX')

    oil.metadata.product_type = "Condensate"
    print(oil)

    # create a sample for fresh oil
    s = Sample()

    # add some densities
    p = s.physical_properties
    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="g/cm^3"),
                     ref_temp=Temperature(value=13.0, unit="C")),
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


def test_check_API_is_there_correct():
    """
    if there is an API, check() should return the empty string
    """
    oil = no_api_with_density()
    oil.metadata.API = 30.06

    fixer = FixAPI(oil)

    flag, msg = fixer.check()

    assert flag is None
    assert "API is fine" in msg


def test_check_API_is_there_mismatch():
    """
    if there is an API, check() should return the empty string
    """
    oil = no_api_with_density()
    oil.metadata.API = 32.0

    fixer = FixAPI(oil)

    flag, msg = fixer.check()

    assert flag is True
    assert "doesn't match density data" in msg


def test_add_density():
    oil = no_api_with_density()

    # before adding:
    assert oil.metadata.API is None

    fixer = FixAPI(oil)

    fixer.cleanup()

    assert isclose(oil.metadata.API, 30.06, rel_tol=1e4)


def test_find_density_at_60F():
    oil = no_api_with_density()
    fixer = FixAPI(oil)
    result = fixer.find_density_at_60F()

    assert result == 875.1


def test_find_density_at_60F_two_values():
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

    result = fixer.find_density_at_60F()

    assert isclose(result, 989.0, rel_tol=1e3)


def test_find_density_at_60F_none():
    """
    if there are no density values, then this should not add an API
    """
    oil = no_api_with_density()

    oil.sub_samples[0].physical_properties.densities = DensityList()
    fixer = FixAPI(oil)

    result = fixer.find_density_at_60F()

    assert result is None


def test_non_crude_one_density_close():
    oil = no_api_with_one_density_13C()

    fixer = FixAPI(oil)
    fixer.cleanup()

    assert isclose(oil.metadata.API, 30.06, rel_tol=1e4)


def test_non_crude_one_density_far():
    # density at too far a temp to compute API
    oil = no_api_with_one_density_13C()
    oil.sub_samples[0].physical_properties.densities[0].ref_temp.value = 0.0

    fixer = FixAPI(oil)
    fixer.cleanup()

    assert oil.metadata.API is None


def test_non_crude_two_densities_straddle_60():
    oil = no_api_with_density()

    oil.metadata.product_type = "Refined Product NOS"

    oil.sub_samples[0].physical_properties.densities[0].ref_temp.value = 0.0
    oil.sub_samples[0].physical_properties.densities[0].ref_temp.unit = 'C'

    oil.sub_samples[0].physical_properties.densities[1].ref_temp.value = 20.0
    oil.sub_samples[0].physical_properties.densities[1].ref_temp.unit = 'C'

    fixer = FixAPI(oil)
    fixer.cleanup()

    assert isclose(oil.metadata.API, 30.06, rel_tol=1e4)


def test_non_crude_two_densities_not_straddle_60():
    oil = no_api_with_density()

    oil.metadata.product_type = "Refined Product NOS"

    oil.sub_samples[0].physical_properties.densities[0].ref_temp.value = 0.0
    oil.sub_samples[0].physical_properties.densities[0].ref_temp.unit = 'C'

    oil.sub_samples[0].physical_properties.densities[1].ref_temp.value = 10.0
    oil.sub_samples[0].physical_properties.densities[1].ref_temp.unit = 'C'

    fixer = FixAPI(oil)
    fixer.cleanup()

    assert oil.metadata.API is None
