"""
cleanups that work with density
"""
import math
from operator import itemgetter

import unit_conversion as uc

from .cleanup import Cleanup


class FixAPI(Cleanup):
    """
    adds (or replaces) the API value, from the density measurements

    NOTE: this could be extended to interpolate, but it that actually needed?
    """
    ID = "001"

    DENSITY_TOL = 1.0  # how close do we need to be to 15C to convert to API

    def check(self):
        """
        checks to see if there is something to fix

        returns: flag, msg

        if nothing is needed, flag is None
        if something can be cleaned up, flag is True
        if something is wrong, but can not be cleaned up, flag is False

        fixme: -- maybe cleanup and validation should be better integrated?
        """
        API = self.oil.metadata.API

        # densities = oil.sub_samples[0].physical_properties.densities
        if API is None:
            density = self.find_density_near_15C()
            if density:
                return (True, f"Cleanup: {self.ID}: No API value provided for {self.oil.oil_id}"
                               " -- can be computed from density")
            else:
                return (False, f"Cleanup: {self.ID}: No API value provided for {self.oil.oil_id}"
                                " -- can NOT be computed from density")

        return None, "API is fine"

    def cleanup(self):
        """
        run this particular cleanup option

        :param oil: an Oil object to act on

        :param do_it=False: flag to tell the cleanup to do its thing. If False,
                            the method returns a message. If True, the action is
                            taken, and the Oil object is altered.

        :returns: a message of what could be done, or what was done.
        """
        density_at_15 = self.find_density_near_15C()

        if density_at_15:
            API = uc.convert("density", "kg/m^3", "API", density_at_15)
            self.oil.metadata.API = round(API, 2)
            return f"Cleanup: {self.ID}: Set API for {self.oil.oil_id} to {API}."

    def check_for_valid_api(self):
        """
        check is the API value is already valid
        """
        API = self.oil.metadata.API

        # densities = self.oil.sub_samples[0].physical_properties.densities

        density_at_15 = self.find_density_near_15C()

        if uc.convert("density", "kg/m^3", "API", density_at_15) == API:
            return True
        else:
            return False

    def build_density_table(self):
        """
        build a density table from the data:
        list of (density, temp) pairs
        """

        densities = self.oil.sub_samples[0].physical_properties.densities

        # create normalized list of densities
        density_table = []
        for density_point in densities:
            d = density_point.density.converted_to("kg/m^3").value
            t = density_point.ref_temp.converted_to("C").value
            density_table.append((d, t))
        return density_table

    def find_density_near_15C(self):
        """
        returns the density (in kg/m3) within DENSITY_TOL of 15C

        Note: this could be cleaner with numpy -- but for so few values?
        """
        density_table = self.build_density_table()
        min_diff = math.inf
        for i, d in enumerate(density_table):
            if d[1] < min_diff:
                min_diff = d[1] - 15.0
                min_ind = i
        if abs(min_diff) <= self.DENSITY_TOL:
            return density_table[min_ind][0]
        else:
            return None









