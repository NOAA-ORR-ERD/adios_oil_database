"""
Cleanup temp-value pairs with missing values
"""

from .cleanup import Cleanup

class TempValueEmpty(Cleanup):
    ID = "004"

    def check(self):
        """
        checks to see if there are any empty  values in a:

        "temperature-value pair" list.

        e.g. viscosity, density, etc...

        returns: flag, msg

        if nothing is needed, flag is None
        if something can be cleaned up, flag is True
        if something is wrong, but can not be cleaned up, flag is False

        fixme: -- maybe cleanup and validation should be better integrated?
        """
        # use validator to see if there's an issue

        msgs = self.oil.validate()

        problems = []
        for msg in msgs:
            if msg.startswith("E048:") or msg.startswith("E049:"):
                problems.append(msg)

        if problems:
            return True, "\n".join(problems)
        else:
            return None, "No missing values in Temp-Value pairs"


    def cleanup(self):
        """
        cleanup option:

        remove empty items from temp-value lists.
        """
        # this could report more detail ...
        temp_val_lists = ["densities",
                          "kinematic_viscosities",
                          "dynamic_viscosities",
                          "interfacial_tension_air",
                          "interfacial_tension_water",
                          "interfacial_tension_seawater",
                          ]
        num_removed = 0
        for ss in self.oil.sub_samples:
            pp = ss.physical_properties
            for tvl_name in temp_val_lists:
                tvl = getattr(pp, tvl_name, None)
                if tvl is not None:
                    num = len(tvl)

                    tvl.delete_empty_values()
                    num_removed += num - len(tvl)
        return (f"Cleanup: {self.ID}: "
                f"Removed {num_removed} empty lines from physical properties data in {self.oil.oil_id}")


