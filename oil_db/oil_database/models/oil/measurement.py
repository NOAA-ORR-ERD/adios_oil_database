'''
    Classes for storing measured values within an Oil record
'''
from dataclasses import dataclass

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import (Temperature,
                                  MassFraction,
                                  Density,
                                  DynamicViscosity,
                                  KinematicViscosity,
                                  InterfacialTension,
                                  Adhesion)


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
class InterfacialTensionPoint:
    interface: str
    tension: InterfacialTension
    ref_temp: Temperature
    method: str = None


class InterfacialTensionList(JSON_List):
    item_type = InterfacialTensionPoint


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
    '''
        Note: This is a first pass attempt.  Will probably need to be
              reorganized.
    '''
    # Pa units, some kind of pressure/stress.
    # Adhesion provides the right units
    complex_modulus: Adhesion
    storage_modulus: Adhesion
    loss_modulus: Adhesion

    # Todo: this seems to be just unit-less float, but it is a measurement
    #       with standard_deviation & replicates.  Well MassFraction will do
    #       for now.  But NUCOS needs to be updated.
    tan_delta: MassFraction

    complex_viscosity: DynamicViscosity
    water_content: MassFraction

    method: str = None
    visual_stability: str = None


class EmulsionList(JSON_List):
    item_type = Emulsion
