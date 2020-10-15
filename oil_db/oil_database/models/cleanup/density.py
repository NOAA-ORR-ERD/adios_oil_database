"""
cleanups that work with density
"""

from .cleanup import Cleanup


class FixAPI(Cleanup):
    """
    adds (or replaces) the API value, from the density measurements
    """
    ID = "001"

    def check(self):
        """
        checks ot see if there is somethign to fix

        if so, a message is returned

        if not, then None is returned

        fixme: there are really three options:
               1) Nothing to fix
               2) Something broken, but not fixable
               3) Something to fix that is fixable
               But 2) should be caught by validation, so not doing it here
                      -- maybe cleanup and validation should be better integrated?
        """
        API = self.oil.metadata.API

        # densities = oil.sub_samples[0].physical_properties.densities
        if API is None:
            density = self.find_density_near_15C()
            if density:
                return f"Cleanup: {self.ID}: No API value provided -- can be computed from density"

        return None


    def cleanup(self):
        """
        run this particular cleanup option

        :param oil: an Oil object to act on

        :param do_it=False: flag to tell the cleanup to do its thing. If False,
                            the method returns a message. If True, the action is
                            taken, and the Oil object is altered.

        :returns: a message of what could be done, or what was done.
        """
        self.check_for_valid_api()

    def check_for_valid_api(self):
        """
        check is the API value is already valid
        """
        API = self.oil.metadata.API

        densities = self.oil.sub_samples[0].physical_properties.densities

        density_at_15 = self.find_density_near_15C()

    def find_density_near_15C(self):
        densities = self.oil.sub_samples[0].physical_properties.densities

        #create normalized list of densities
        density_table = []
        for density_point in densities:
            print(density_point)
            d = density_point.density
            t = density_point.ref_temp
            density_table.append((d, t))
        print(density_table)









