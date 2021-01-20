"""
utilities for doing computation on the physical properties of an
oil record
"""


def get_density_data(oil, density_units="kg/m^3", temp_units="K"):
    """
    Return a table of density data:

    list of (density, temp) pairs

    :param oil: the oil object to get data from

    :param density_units="kg/m^3": units you want the density in

    :param temp_units="K": units you want the density in

    """

    densities = oil.sub_samples[0].physical_properties.densities

    # create normalized list of densities
    density_table = []
    for density_point in densities:
        d = density_point.density.converted_to(density_units).value
        t = density_point.ref_temp.converted_to(temp_units).value
        density_table.append((d, t))
    return density_table


def get_kinematic_viscosity_at_temp(temp,
                                    kvis_units='cSt',
                                    temp_units='C'):
    raise NotImplementedError




