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
        pass

    def cleanup(self):
        """
        run this particular cleanup option

        :param oil: an Oil object to act on

        :param do_it=False: flag to tell the cleanup to do its thing. If False,
                            the method returns a message. If True, the action is
                            taken, and the Oil object is altered.

        :returns: a message of what could be done, or what was done.
        """
        self.check_for_valid_api(oil)

    def check_for_valid_api(self, oil):
        """
        check is the API value is already valid
        """
        API = oil.metadata.API

        densities = oil.sub_samples[0].physical_properties.densities

        if API is None:
            return [f"Cleanup: {self.ID}: No API value provided"]

    def find_density_near_15C(self):
        pass
