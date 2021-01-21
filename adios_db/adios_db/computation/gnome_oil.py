"""
Code for making a "GnomeOil" from an Oil Object

NOTE: This make s JSON compatible Python structure from. which to build a GnomeOil

"""

from .physical_properties import get_density_data


def get_empty_dict():
    return{"name": "",
           # Physical properties
           "api": None,
           "pour_point": None,
           "solubility": None,  # kg/m^3
           # emulsification properties
           "bullwinkle_fraction": None,
           "bullwinkle_time": None,
           "emulsion_water_fraction_max": None,
           "densities": [],
           "density_ref_temps": [],
           "density_weathering": [],
           "kvis": [],
           "kvis_ref_temps": [],
           "kvis_weathering": [],
           # PCs:
           "mass_fraction": [],
           "boiling_point": [],
           "molecular_weight": [],
           "component_density": [],
           "sara_type": [],
           "flash_point": None,
           "adios_oil_id": None,
           }

def make_gnome_oil(oil):
    """
    Make a dict that a GnomeOil can be built from

    A GnomeOil needs:

              "name,
              "# Physical properties
              "api,
              "pour_point,
              "solubility,  # kg/m^3
              "# emulsification properties
              "bullwinkle_fraction,
              "bullwinkle_time,
              "emulsion_water_fraction_max,
              "densities,
              "density_ref_temps,
              "density_weathering,
              "kvis,
              "kvis_ref_temps,
              "kvis_weathering,
              "# PCs:
              "mass_fraction,
              "boiling_point,
              "molecular_weight,
              "component_density,
              "sara_type,
              "flash_point=None,
              "adios_oil_id=None,

    """

    # metadata:
    go = get_empty_dict()
    go['name'] = oil.metadata.name
    go['api'] = oil.metadata.API
    go['adios_oil_id'] = oil.oil_id

    #. Physical properties
    phys_props = oil.sub_samples[0].physical_properties

    go['flash_point'] = phys_props.flash_point.measurement.converted_to('K').max_value
    go['pour_point'] = phys_props.pour_point.measurement.converted_to('K').max_value

    # fixme: We need to get the weathered densities, if they are there.
    densities = get_density_data(oil, units="kg/m^3", temp_units="K")

    go['densities'], go['density_ref_temps'] = zip(*densities)
    go['density_weathering'] = [0.0] * len(go['densities'])

    return go






