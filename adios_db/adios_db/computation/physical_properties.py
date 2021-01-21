"""
utilities for doing computation on the physical properties of an
oil record
"""

from operator import itemgetter
import numpy as np


def get_density_data(oil, units="kg/m^3", temp_units="K"):
    """
    Return a table of density data:

    list of (density, temp) pairs

    :param oil: the oil object to get data from

    :param units="kg/m^3": units you want the density in

    :param temp_units="K": units you want the density in

    """

    densities = oil.sub_samples[0].physical_properties.densities

    # create normalized list of densities
    density_table = []
    for density_point in densities:
        d = density_point.density.converted_to(units).value
        t = density_point.ref_temp.converted_to(temp_units).value
        density_table.append((d, t))
    return density_table


def get_kinematic_viscosity_data(oil, units="cSt", temp_units="K"):

    """
    Return a table of kinematic viscosity data:

    list of (viscosity, temp) pairs

    :param oil: the oil object to get data from

    :param units="cSt": units you want the viscosity in

    :param temp_units="K": units you want the viscosity in

    """

    kvisc = oil.sub_samples[0].physical_properties.kinematic_viscosities

    if len(kvisc) > 0:
        visc_table = []
        for visc_point in viscosities:
            d = visc_point.viscosity.converted_to(units).value
            t = visc_point.ref_temp.converted_to(temp_units).value
            visc_table.append((d, t))
        return visc_table

    dvisc = oil.sub_samples[0].physical_properties.dynamic_viscosities
    if len(dvisc) > 0:
        dvisc = get_dynamic_viscosity_data(oil, units="cP", temp_units="K")
        densities = get_density_data(oil, units="g/cm^3", temp_units="K")
        visc_table = convert_dvisc_to_kvisc(dvisc, densities)
        return visc_table
    else:
        return []

def get_dynamic_viscosity_data(oil, units="cP", temp_units="K"):

    """
    Return a table of kinematic viscosity data:

    list of (viscosity, temp) pairs

    :param oil: the oil object to get data from

    :param units="cSt": units you want the viscosity in

    :param temp_units="K": units you want the viscosity in

    """

    dvisc = oil.sub_samples[0].physical_properties.dynamic_viscosities

    if len(dvisc) > 0:
        visc_table = []
        for visc_point in dvisc:
            v = visc_point.viscosity.converted_to(units).value
            t = visc_point.ref_temp.converted_to(temp_units).value
            visc_table.append((v, t))
        return visc_table

    kvisc = oil.sub_samples[0].physical_properties.kinematic_viscosities
    if len(kvisc) > 0:
        raise NotImplementedError("can't compute dynamic from kinematic yet")
        kvisc = get_kinematic_viscosity_data(oil)
        # convert here.
    else:
        return []


def convert_dvisc_to_kvisc(dvisc, densities):
    """
    convert dynamic viscosity to kinematic viscosity

    dvisc and densities are tables as returned from:
      get_dynamic_viscosity_data
      get_density_data
    units: cP, g/cm^3, K
    """
    kvisc_table = []
    for (dv, temp) in dvisc:
        kv = dv / density_at_temp(densities, temp)
        kvisc_table.append((kv, temp))
    return kvisc_table


def density_at_temp(densities, temp, units="kg/m^3", temp_units="K"):
    # sort them to make sure
    densities = sorted(densities, key=itemgetter(1))
    dens, temps = zip(*densities)

    return np.interp(temp, temps, dens)



def get_kinematic_viscosity_at_temp(temp,
                                    kvis_units='cSt',
                                    temp_units='C'):
    raise NotImplementedError




