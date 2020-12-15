"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List

from oil_database.models.common.measurement import (Temperature,
                                                    Density,
                                                    DynamicViscosity,
                                                    KinematicViscosity,
                                                    AngularVelocity,
                                                    InterfacialTension
                                                    )


@dataclass_to_json
@dataclass
class DensityPoint:
    density: Density
    ref_temp: Temperature
    method: str = None


class DensityList(JSON_List):
    item_type = DensityPoint


@dataclass_to_json
@dataclass
class DynamicViscosityPoint:
    viscosity: DynamicViscosity
    ref_temp: Temperature
    shear_rate: AngularVelocity = None
    method: str = None


class DynamicViscosityList(JSON_List):
    item_type = DynamicViscosityPoint


@dataclass_to_json
@dataclass
class KinematicViscosityPoint:
    viscosity: KinematicViscosity
    ref_temp: Temperature
    shear_rate: AngularVelocity = None
    method: str = None


class KinematicViscosityList(JSON_List):
    item_type = KinematicViscosityPoint


@dataclass_to_json
@dataclass
class PourPoint:
    measurement: Temperature = None
    method: str = None


@dataclass_to_json
@dataclass
class FlashPoint:
    measurement: Temperature = None
    method: str = None


@dataclass_to_json
@dataclass
class InterfacialTensionPoint:
    tension: InterfacialTension
    ref_temp: Temperature
    interface: str = None
    method: str = None


class InterfacialTensionList(JSON_List):
    item_type = InterfacialTensionPoint


@dataclass_to_json
@dataclass
class PhysicalProperties:
    pour_point: PourPoint = None
    flash_point: FlashPoint = None

    densities: DensityList = field(default_factory=DensityList)
    kinematic_viscosities: KinematicViscosityList = field(default_factory=KinematicViscosityList)
    dynamic_viscosities: DynamicViscosityList = field(default_factory=DynamicViscosityList)

    interfacial_tension_air: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_water: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_seawater: InterfacialTensionList = field(default_factory=InterfacialTensionList)

