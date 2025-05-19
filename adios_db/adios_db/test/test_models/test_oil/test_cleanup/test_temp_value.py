from adios_db.models.oil.cleanup.temp_value import TempValueEmpty

from adios_db.models.common.measurement import Density, Temperature
from adios_db.models.oil.oil import Oil
from adios_db.models.oil.physical_properties import DensityPoint, DensityList
from adios_db.models.oil.sample import Sample

def no_missing_values():
    oil = Oil(oil_id='XXXXXX')

    oil.metadata.product_type = "Crude Oil NOS"

    # create a sample for fresh oil
    s = Sample()

    # add some densities
    p = s.physical_properties
    p.densities = DensityList([
        DensityPoint(density=Density(value=0.8751, unit="g/cm^3"),
                     ref_temp=Temperature(value=60.0, unit="F")),
        DensityPoint(density=Density(value=0.99, unit="g/cm^3"),
                     ref_temp=Temperature(value=25.0, unit="C")),
        DensityPoint(density=Density(value=0.96, unit="g/cm^3"),
                     ref_temp=Temperature(value=50.0, unit="C")),

    ])

    oil.sub_samples.append(s)

    return oil


def test_nothing_wrong():
    oil = no_missing_values()
    tvs = TempValueEmpty(oil)

    result = tvs.check()
    assert result[0] is None

    assert result[1] == 'No missing values in Temp-Value pairs'


def test_check_two_values_missing():
    oil = no_missing_values()

    densities = oil.sub_samples[0].physical_properties.densities


    densities[0].ref_temp = None
    densities[1].density = None

    tvs = TempValueEmpty(oil)

    result = tvs.check()
    print(result)

    assert result[0] is True

    assert len(result[1].split("\n")) == 2


def test_cleanup_two_values_missing():
    oil = no_missing_values()

    densities = oil.sub_samples[0].physical_properties.densities


    densities[0].ref_temp = None
    densities[1].density = None

    tvs = TempValueEmpty(oil)


    result = tvs.cleanup()


    assert len(oil.sub_samples[0].physical_properties.densities) == 1
    assert "Removed 2 empty lines" in result
