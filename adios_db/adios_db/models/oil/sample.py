"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import VolumeFraction

from .distillation import Distillation
from .metadata import SampleMetaData
from .physical_properties import PhysicalProperties
from .environmental_behavior import EnvironmentalBehavior
from .sara import Sara
from .ests_fractions import ESTSFractions

# need the namespace for ccme, as using the fieldname the same as the class
# breaks things.
from . import ccme
from .compound import CompoundList
from .industry_property import IndustryPropertyList
from .bulk_composition import BulkCompositionList

from .validation.warnings import WARNINGS
from .validation.errors import ERRORS


@dataclass_to_json
@dataclass
class Sample:
    """
    represents the physical and chemical properties of particular sub sample.

    could be fresh oil, or weathered samples, or distillation cuts, or ...
    """
    metadata: SampleMetaData = field(default_factory=SampleMetaData)

    cut_volume: VolumeFraction = None  # from Exxon data

    physical_properties: PhysicalProperties = field(
        default_factory=PhysicalProperties
    )

    environmental_behavior: EnvironmentalBehavior = field(
        default_factory=EnvironmentalBehavior
    )

    SARA: Sara = field(default_factory=Sara)

    distillation_data: Distillation = field(default_factory=Distillation)

    compounds: CompoundList = field(default_factory=CompoundList)

    bulk_composition: BulkCompositionList = field(
        default_factory=BulkCompositionList
    )

    industry_properties: IndustryPropertyList = field(
        default_factory=IndustryPropertyList
    )

    headspace_analysis: CompoundList = field(default_factory=CompoundList)

    CCME: ccme.CCME = field(default_factory=ccme.CCME)

    ESTS_hydrocarbon_fractions: ESTSFractions = None

    miscellaneous: CompoundList = field(default_factory=CompoundList)

    # a place to store arbitrary extra data.
    extra_data: dict = field(default_factory=dict)

    def __post_init__(self):
        metadata = self.metadata

        # fixme -- this should not be built in to the object!!
        if metadata.name is not None:
            if metadata.name.lower() == 'whole crude':
                metadata.name = 'Fresh Oil Sample'

        if metadata.short_name is None and metadata.name is not None:
            if metadata.name.lower() == 'fresh oil sample':
                metadata.short_name = 'Fresh Oil'
            else:
                metadata.short_name = f'{metadata.name[:12]}...'

    def __repr__(self):
        return f"sample: {self.metadata.name}\n{self.metadata.description}"


class SampleList(JSON_List):
    item_type = Sample

    def validate(self):
        msgs = []

        if len(self) == 0:  # at least one subsample?
            msgs.append(ERRORS["E031"])
        else:
            # Check for densities
            # NOTE: would be good to be smart about the temp densities are at
            # This is here because only need to check the "fresh" sample
            if (self[0].physical_properties is None
                    or not self[0].physical_properties.densities):
                # warning if no density in zeroth subample
                msgs.append(WARNINGS["W006"])

            short_names = [ss.metadata.short_name for ss in self]
            names = [ss.metadata.name for ss in self]

            # find duplicates
            seen = set()
            dupes = [x for x in short_names if x in seen or seen.add(x)]
            if dupes:
                msgs.append(ERRORS["E051"].format(dupes))
            seen = set()
            dupes = [x for x in names if x in seen or seen.add(x)]
            if dupes:
                msgs.append(ERRORS["E052"].format(dupes))

            # # check_for_distillation_cuts
            # try:
            #     if not self[0].distillation_data.cuts:
            #         msgs.append(WARNINGS['W007'])
            # except AttributeError:
            #     msgs.append(WARNINGS['W007'])



        # validate all the subsamples
        for ss in self:
            msgs.extend(ss.validate())
        return msgs
