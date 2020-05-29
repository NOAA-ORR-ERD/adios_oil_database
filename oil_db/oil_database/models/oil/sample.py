"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List

from ..common.measurement import MassFraction, VolumeFraction, Temperature
from .measurement import Distillation

from .physical_properties import PhysicalProperties
from .environmental_behavior import EnvironmentalBehavior
from .sara import Sara
from .ccme import CCME
from .ests_fractions import ESTSFractions

from .compound import CompoundList


@dataclass_to_json
@dataclass
class Sample:
    """
    represents the physical and chemical properties of particular sub sample.

    could be fresh oil, or weathered samples, or distillation cuts, or ...
    """
    # metadata:
    name: str = "Fresh Oil Sample"
    short_name: str = None
    fraction_weathered: MassFraction = None
    boiling_point_range: Temperature = None
    cut_volume: VolumeFraction = None  # from Exxon data

    physical_properties: PhysicalProperties = None
    environmental_behavior: EnvironmentalBehavior = None
    SARA: Sara = None

    distillation_data: Distillation = field(default_factory=Distillation)

    compounds: CompoundList = field(default_factory=CompoundList)

    bulk_composition: CompoundList = field(default_factory=CompoundList)

    industry_properties: CompoundList = field(default_factory=CompoundList)

    headspace_analysis: CompoundList = field(default_factory=CompoundList)

    CCME: CCME = None

    ESTS_hydrocarbon_fractions: ESTSFractions = None

    miscellaneous: CompoundList = field(default_factory=CompoundList)

    # Assorted:

    # From Exxon Dist cut data

    extra_data: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.name is not None:
            if self.name.lower() == 'whole crude':
                self.name = 'Fresh Oil Sample'

        if self.short_name is None and self.name is not None:
            if self.name.lower() == 'fresh oil sample':
                self.short_name = 'Fresh Oil'
            else:
                self.short_name = f'{self.name[:12]}...'


class SampleList(JSON_List):
    item_type = Sample
