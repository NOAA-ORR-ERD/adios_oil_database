'''
    Classes for storing measured values within an Oil record
'''
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import (Time,
                                  Temperature,
                                  MassFraction,
                                  Unitless,
                                  Dimensionless,
                                  Density,
                                  DynamicViscosity,
                                  KinematicViscosity,
                                  InterfacialTension,
                                  NeedleAdhesion,
                                  AngularVelocity)


@dataclass_to_json
@dataclass
class DensityPoint:
    density: Density
    ref_temp: Temperature


class DensityList(JSON_List):
    item_type = DensityPoint


@dataclass_to_json
@dataclass
class DynamicViscosityPoint:
    viscosity: DynamicViscosity
    ref_temp: Temperature
    shear_rate: AngularVelocity = None


class DynamicViscosityList(JSON_List):
    item_type = DynamicViscosityPoint


@dataclass_to_json
@dataclass
class KinematicViscosityPoint:
    viscosity: KinematicViscosity
    ref_temp: Temperature


class KinematicViscosityList(JSON_List):
    item_type = KinematicViscosityPoint


@dataclass_to_json
@dataclass
class DistCut:
    fraction: MassFraction
    vapor_temp: Temperature


class DistCutList(JSON_List):
    """
    needs some refactoring: should be method, for one
    """
    item_type = DistCut

    def validate(self):
        # do validation here
        pass


@dataclass_to_json
@dataclass
class Distillation:
    type: str = None
    method: str = None
    end_point: Temperature = None
    cuts: DistCutList = field(default_factory=DistCutList)


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
class Dispersibility:
    dispersant: str
    effectiveness: MassFraction
    method: str = None


class DispersibilityList(JSON_List):
    item_type = Dispersibility


@dataclass_to_json
@dataclass
class Emulsion:
    age: Time
    water_content: MassFraction

    # Pa units, some kind of pressure/stress.
    # Adhesion provides the right units
    complex_modulus: NeedleAdhesion = None
    storage_modulus: NeedleAdhesion = None
    loss_modulus: NeedleAdhesion = None

    # Todo: this seems to be just unit-less float, but it is a measurement
    #       with standard_deviation & replicates.  Well MassFraction will do
    #       for now.  But NUCOS needs to be updated.
    tan_delta_v_e: Unitless = None

    complex_viscosity: DynamicViscosity = None

    method: str = None
    visual_stability: str = None


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
