"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json

from ..common.measurement import Temperature
from .measurement import (DensityList,
                          DynamicViscosityList,
                          KinematicViscosityList,
                          InterfacialTensionList)


@dataclass_to_json
@dataclass
class PhysicalProperties:
    pour_point: Temperature = None
    flash_point: Temperature = None

    densities: DensityList = field(default_factory=DensityList)
    kinematic_viscosities: KinematicViscosityList = field(default_factory=KinematicViscosityList)
    dynamic_viscosities: DynamicViscosityList = field(default_factory=DynamicViscosityList)

    interfacial_tensions: InterfacialTensionList = field(default_factory=InterfacialTensionList)
