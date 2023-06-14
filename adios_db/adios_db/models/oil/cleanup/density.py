"""
cleanups that work with density
"""
import nucos as uc

from .cleanup import Cleanup

from ....computation.physical_properties import Density

# product types that we will arbitrarily extrapolate
# others will only be extrapolated if their is one density value
# close to 60F, or two values bracketing 60F

CRUDE_PRODUCTS = {"Crude Oil NOS",
                  "Tight Oil"}


class FixAPI(Cleanup):
    """
    adds (or replaces) the API value, from the density measurements
    """
    ID = "001"

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
        is_valid = self.check_for_valid_api()
        density = self.find_density_at_60F()

        msg = ("No API value provided for "
               if API is None else
               f"API: {API} doesn't match density data for "
               )

        if API is None or not is_valid:
            if density:
                return (True, f"Cleanup: {self.ID}: {msg}"
                              f"{self.oil.oil_id}"
                              " -- can be computed from density")
            else:
                return (False, f"Cleanup: {self.ID}: {msg}"
                               f"{self.oil.oil_id}"
                               " -- can NOT be computed from density")
        else:
            return None, "API is fine"

    def cleanup(self):
        """
        run this particular cleanup option

        :param oil: an Oil object to act on

        # :param do_it=False: flag to tell the cleanup to do its thing.
        #                     If False, the method returns a message. If True,
        #                     the action is taken, and the Oil object is altered.

        :returns: a message of what could be done, or what was done.
        """
        density_at_60 = self.find_density_at_60F()

        if density_at_60:
            API = uc.convert("density", "kg/m^3", "API", density_at_60)
            self.oil.metadata.API = round(API, 2)

            return (f"Cleanup: {self.ID}: "
                    f"Set API for {self.oil.oil_id} to {API}.")

    def check_for_valid_api(self):
        """
        Check is the API value is already valid
        """
        API = self.oil.metadata.API

        if API is None:
            return False

        density_at_60F = self.find_density_at_60F()

        if density_at_60F is None:
            return None

        computed_API = uc.convert("density", "kg/m^3", "API", density_at_60F)

        if abs(API - computed_API) <= 0.2:
            return True
        else:
            return False

    def find_density_at_60F(self):
        """
        Returns the density (in kg/m3)

        It will interpolate and extrapolate as needed
        """
        try:
            density = Density(self.oil)
            have_data = False
            if self.oil.metadata.product_type in CRUDE_PRODUCTS:
                have_data = True
            else:
                temps = density.temps\

                if len(temps) == 1:
                    t = temps[0]
                    if 286 < t < 291:  # 55F, 65F (is the value near 60F?)
                        have_data = True
                else:
                    # check if ref temps are anywhere near 60F
                    if (max(temps) >= 286 and min(temps) <= 291):
                        have_data = True

            if have_data:
                return density.at_temp(uc.convert("F", "K", 60))
        except Exception:  # something went wrong, and we don't want it to barf
            return None
