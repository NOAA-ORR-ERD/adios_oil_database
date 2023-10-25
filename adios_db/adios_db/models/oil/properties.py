"""
Classes for storing measured values within an Oil record
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import (Time,
                                  Temperature,
                                  MassFraction,
                                  Unitless,
                                  DynamicViscosity,
                                  InterfacialTension,
                                  Pressure)
from .physical_properties import DynamicViscosityList, KinematicViscosityList

from ..common.validators import EnumValidator
from .validation.errors import ERRORS


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
class Dispersibility:
    dispersant: str = None
    effectiveness: MassFraction = None
    method: str = None


class DispersibilityList(JSON_List):
    item_type = Dispersibility


@dataclass_to_json
@dataclass
class Emulsion:
    """
    There is no use for an empty Emulsion object

    But there is a use for one that has an arbitrary subset of fields,

    so making them all optional
    """
    age: Time = None
    water_content: MassFraction = None

    ref_temp: Temperature = None

    # Pa units, some kind of pressure/stress.
    # Adhesion provides the right units
    # but we shouldn't use it - so Pressure?
    complex_modulus: Pressure = None
    storage_modulus: Pressure = None
    loss_modulus: Pressure = None

    tan_delta_v_e: Unitless = None

    complex_viscosity: DynamicViscosity = None

    kinematic_viscosities: KinematicViscosityList = field(default_factory=KinematicViscosityList)
    dynamic_viscosities: DynamicViscosityList = field(default_factory=DynamicViscosityList)

    method: str = None
    visual_stability: str = None

    def validate(self):
        msgs = []
        if self.visual_stability is not None:
            msgs.extend(EnumValidator({"Stable", "Mesostable", "Unstable",
                                       "Entrained", "Did not form", "Unknown"},
                                      ERRORS["E033"],
                                      case_insensitive=False)(self.visual_stability))

        return msgs


class EmulsionList(JSON_List):
    item_type = Emulsion


@dataclass_to_json
@dataclass
class ESTSEvaporationTest:
    a_for_ev_a_b_ln_t_c: float = None
    a_for_ev_a_b_ln_t: float = None
    a_for_ev_a_b_sqrt_t: float = None
    b_for_ev_a_b_ln_t_c: float = None
    b_for_ev_a_b_ln_t: float = None
    b_for_ev_a_b_sqrt_t: float = None
    c_for_ev_a_b_ln_t_c: float = None
    method: str = None
