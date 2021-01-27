"""
utilities for doing computation on the physical properties of an
oil record
"""

from operator import itemgetter
from math import isclose
import numpy as np


import unit_conversion as uc


class Density:
    """
    class to hold and do calculations on density

    data is stored internally in standard units:
    temperature in Kelvin
    density in kg/m^3
    """
    def __init__(self, oil):
        """
        Initialize a density calculator

        :param oil: an Oil object -- the density data will be extracted

        or

        :param oil: Sequence of density/temperature pairs:
                    ``[(980.0, 288.15), (990.0, 273.15)])``

        If data pairs, units must be kg/m^3 and K
        """
        try:
            data = get_density_data(oil, units='kg/m^3', temp_units="K")
        except AttributeError:
            # not an oil object -- assume it's a table of data in the correct form
            data = oil
        data = sorted(data, key=itemgetter(1))
        self.densities, self.temps = zip(*data)
        self.initialize()

    def initialize(self):
        """
        Initialize the expansion coefficient

        For outside the measured range
        """
        # if there is only one density, use a default
        # Note: no idea where these values came from

        if not np.all(np.diff(self.temps) > 0):
            raise ValueError("temperatures must be discreet")

        if len(self.densities) == 1:
            d = self.densities[0]
            t = self.temps[0]
            if abs(t - 288.16) < 5.0:  # measurement within 5 deg of 15 C
                # API 30 threshold
                self.k_rho_default = 0.0009 if d < 875 else 0.0008
            else:
                self.k_rho_default = 0.00085  # who knows?
        elif len(self.densities) > 1:
            # do a linear fit to the points
            # this should exactly match if there are only two.
            b = self.densities
            A = np.c_[np.ones_like(b), np.array(self.temps)]
            x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
            self.k_rho_default = x[1]
        else:
            raise ValueError("Density needs at least one density value")

    def at_temp(self, temp):
        """
        density(s) at the provided temperature(s)

        :param temp: scalar or sequence of temp in K

        densities will be returned as kg/m^3
        """
        temp = np.asarray(temp)
        scaler = True if temp.shape == () else False
        temp.shape = (-1,)

        densities = np.interp(temp,
                              self.temps,
                              self.densities,
                              left=-np.inf,
                              right=np.inf)

        left = (densities == -np.inf)
        densities[left] = self.densities[0] + (self.k_rho_default * (temp[left] - self.temps[0]))

        right = (densities == np.inf)
        densities[right] = self.densities[-1] + (self.k_rho_default * (temp[right] - self.temps[-1]))

        return densities if not scaler else densities[0]


class KinematicViscosity:
    """
    class to hold and do calculations on kinematic viscosity

    data is stored internally in standard units:
    temperature in Kelvin
    viscosity in m^2/s
    """
    def __init__(self, oil):
        """
        initialize from an oil object
        """
        data = get_kinematic_viscosity_data(oil, units='m^2/s', temp_units="K")
        self.kviscs, self.temps = zip(*data)
        self.determine_visc_constants()

    def at_temp(self, temp, kvisc_units='m^2/s', temp_units="K"):
        """
        Compute the kinematic viscosity of the oil as a function of temperature

        :param temp_k: temperatures to compute at: can be scalar or array of values.
                       should be in Kelvin

        viscosity as a function of temp is given by:
        v = A exp(k_v2 / T)

        with constants determined from measured data
        """
        temp = np.asarray(temp)
        temp = uc.convert('temperature', temp_units, 'K', temp)

        kvisc = self._visc_A * np.exp(self._k_v2 / temp)

        kvisc = uc.convert('kinematic viscosity', 'm^2/s', kvisc_units, kvisc)
        return kvisc

    def determine_visc_constants(self):
        '''
        viscosity as a function of temp is given by:

        v = A exp(k_v2 / T)

        The constants, A and k_v2 are determined from the viscosity data:

        If only one data point, a default value for k_vs is used:
           2100 K, based on analysis of data in the ADIOS database as of 2018

        If two data points, the two constants are directly computed

        If three or more, the constants are computed by a least squares fit.
        '''
        # find viscosity measurements with zero weathering

        # this sets:
        self._k_v2 = None # decay constant for viscosity curve
        self._visc_A = None

        kvis = self.kviscs
        kvis_ref_temps = self.temps

        if len(kvis) == 1:  # use default k_v2
            self._k_v2 = 2100.0
            self._visc_A = kvis[0] * np.exp(-self._k_v2 / kvis_ref_temps[0])
        else:
            # do a least squares fit to the data
            # viscs = np.array(kvis)
            # temps = np.array(kvis_ref_temps)
            b = np.log(kvis)
            A = np.c_[np.ones_like(b), 1.0 / np.array(kvis_ref_temps)]
            x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
            self._k_v2 = x[1]
            self._visc_A = np.exp(x[0])
        return


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


def get_kinematic_viscosity_data(oil, units="m^2/s", temp_units="K"):

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


def get_dynamic_viscosity_data(oil, units="PaS", temp_units="K"):

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




