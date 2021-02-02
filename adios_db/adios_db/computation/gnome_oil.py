"""
Code for making a "GnomeOil" from an Oil Object

NOTE: This make s JSON compatible Python structure from. which to build a GnomeOil

"""

import numpy as np
from .physical_properties import get_density_data, bullwinkle_fraction, get_kinematic_viscosity_data, get_distillation_cuts
from .estimations import pour_point_from_kvis, flash_point_from_bp, flash_point_from_api


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
           "kvis": [],  # m/s^2
           "kvis_ref_temps": [],  # K
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

    flash_point = phys_props.flash_point
    if flash_point is None:
        go['flash_point'] = estimate_flash_point(oil)
    else:
        if phys_props.flash_point.measurement.max_value is not None:
            go['flash_point'] = phys_props.flash_point.measurement.converted_to('K').max_value
        else
            go['flash_point'] = phys_props.flash_point.measurement.converted_to('K').value

    pour_point = phys_props.pour_point
    if pour_point is None:
        go['pour_point'] = estimate_pour_point(oil)
    else:
        if phys_props.pour_point.measurement.max_value is not None:
            go['pour_point'] = phys_props.pour_point.measurement.converted_to('K').max_value
        else
            go['pour_point'] = phys_props.pour_point.measurement.converted_to('K').value

    # fixme: We need to get the weathered densities, if they are there.
    densities = get_density_data(oil, units="kg/m^3", temp_units="K")

    viscosities = get_kinematic_viscosity_data(oil, units="m^2/s", temp_units="K")

    go['densities'], go['density_ref_temps'] = zip(*densities)
    go['density_weathering'] = [0.0] * len(go['densities'])

    go['kvis'], go['kvis_ref_temps'] = zip(*viscosities)
    go['kvis_weathering'] = [0.0] * len(go['kvis'])

    go['bullwinkle_fraction'] = bullwinkle_fraction(oil)
    go['emulsion_water_fraction_max'] = .9	# for now
    go['solubility'] = 0
    go['k0y'] = 2.024e-06 #do we want this included?
    
    return go


def estimate_pour_point(oil):
    """
    estimate pour point from kinematic viscosity

    """

    pour_point = None
    kvis = get_kinematic_viscosity_data(oil)
    c_v1 = 5000.0
    if kvis:
        lowest_kvis = kvis[0]

        #pour_point = pour_point_from_kvis(lowest_kvis[0], lowest_kvis[1])
        pour_point = (c_v1 * lowest_kvis[1]) / (c_v1 - lowest_kvis[1] * np.log(lowest_kvis[0]))

    return pour_point 


def estimate_flash_point(oil):
    """
    estimate flash point from api or boiling point

    """

    oil_api = oil.metadata.API
    #flash_point = None

    cuts = get_distillation_cuts(oil)

    if len(cuts) > 2:
        #cut_temps = get_cut_temps(oil)
        lowest_cut = cuts[0]
        flash_point = flash_point_from_bp(lowest_cut[1])
    elif oil_api is not None:
        flash_point = flash_point_from_api(oil_api)
    else:
        #est_api = est.api_from_density(density_at_temp(288.15))
        #flash_point = flash_point_from_api(est_api)
        flash_point = None

    return flash_point

