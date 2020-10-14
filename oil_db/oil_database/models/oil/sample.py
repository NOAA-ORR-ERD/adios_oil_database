"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List

from ..common.measurement import MassFraction, VolumeFraction, Temperature

from .measurement import Distillation
from .metadata import SampleMetaData
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
    metadata: SampleMetaData = field(default_factory=SampleMetaData)

    cut_volume: VolumeFraction = None  # from Exxon data

    physical_properties: PhysicalProperties = field(default_factory=PhysicalProperties)
    environmental_behavior: EnvironmentalBehavior = field(default_factory=EnvironmentalBehavior)
    SARA: Sara = field(default_factory=Sara)

    distillation_data: Distillation = field(default_factory=Distillation)

    compounds: CompoundList = field(default_factory=CompoundList)

    bulk_composition: CompoundList = field(default_factory=CompoundList)

    industry_properties: CompoundList = field(default_factory=CompoundList)

    headspace_analysis: CompoundList = field(default_factory=CompoundList)

    CCME: CCME = field(default_factory=CCME)

    ESTS_hydrocarbon_fractions: ESTSFractions = None

    miscellaneous: CompoundList = field(default_factory=CompoundList)

    # a place to store arbitrary extra data.
    extra_data: dict = field(default_factory=dict)

    def __post_init__(self):
        metadata = self.metadata
        if metadata.name is not None:
            if metadata.name.lower() == 'whole crude':
                metadata.name = 'Fresh Oil Sample'

        if metadata.short_name is None and metadata.name is not None:
            if metadata.name.lower() == 'fresh oil sample':
                metadata.short_name = 'Fresh Oil'
            else:
                metadata.short_name = f'{self.name[:12]}...'


class SampleList(JSON_List):
    item_type = Sample
